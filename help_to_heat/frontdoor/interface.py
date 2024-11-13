import ast
import logging
from http import HTTPStatus

import marshmallow
import osdatahub
import requests
from django.conf import settings

from help_to_heat import portal
from help_to_heat.utils import Entity, Interface, register_event, with_schema

from . import models, schemas
from .consts import (
    all_pages,
    confirm_and_submit_page,
    epc_accept_suggested_epc_field,
    epc_accept_suggested_epc_field_not_found,
    epc_rating_field,
    epc_rating_field_not_found,
    field_yes,
    loft_access_field,
    loft_access_field_no_loft,
    loft_field,
    loft_field_no,
    loft_insulation_field,
    loft_insulation_field_less_than_threshold,
    loft_insulation_field_no_insulation,
    loft_insulation_field_no_loft,
    park_home_main_residence_field,
    property_subtype_field,
    property_type_field,
    property_type_field_park_home,
    supplier_field,
)
from .epc_api import EPCApi
from .os_api import OSApi, ThrottledApiException
from .routing import calculate_journey


class SaveAnswerSchema(marshmallow.Schema):
    session_id = marshmallow.fields.UUID()
    page_name = marshmallow.fields.String(validate=marshmallow.validate.OneOf(all_pages))
    data = marshmallow.fields.Nested(schemas.SessionSchema(unknown=marshmallow.EXCLUDE))


class RemoveAnswerSchema(marshmallow.Schema):
    session_id = marshmallow.fields.UUID()
    page_name = marshmallow.fields.String(validate=marshmallow.validate.OneOf(all_pages))


class GetAnswerSchema(marshmallow.Schema):
    session_id = marshmallow.fields.UUID()
    page_name = marshmallow.fields.String(validate=marshmallow.validate.OneOf(all_pages))


class GetPageAnswersSchema(marshmallow.Schema):
    session_id = marshmallow.fields.UUID()
    page_name = marshmallow.fields.String(validate=marshmallow.validate.OneOf(all_pages))


class GetSessionSchema(marshmallow.Schema):
    session_id = marshmallow.fields.UUID()


class CreateReferralSchema(marshmallow.Schema):
    session_id = marshmallow.fields.UUID()


class ReferralSchema(marshmallow.Schema):
    id = marshmallow.fields.UUID()
    session_id = marshmallow.fields.UUID()
    data = marshmallow.fields.Nested(schemas.SessionSchema(unknown=marshmallow.EXCLUDE))


class FindAddressesSchema(marshmallow.Schema):
    building_name_or_number = marshmallow.fields.String()
    postcode = marshmallow.fields.String()


class GetAddressSchema(marshmallow.Schema):
    uprn = marshmallow.fields.String()


class GetEPCSchema(marshmallow.Schema):
    rrn = marshmallow.fields.String()


class AddressSchema(marshmallow.Schema):
    uprn = marshmallow.fields.String()
    address_line_1 = marshmallow.fields.String()
    address_line_2 = marshmallow.fields.String()
    town = marshmallow.fields.String()
    postcode = marshmallow.fields.String()
    local_custodian_code = marshmallow.fields.String()


class FullAddressSchema(marshmallow.Schema):
    uprn = marshmallow.fields.String()
    address = marshmallow.fields.String()


class GetScottishEPCSchema(marshmallow.Schema):
    uprn = marshmallow.fields.String()


class EPCSchema(marshmallow.Schema):
    uprn = marshmallow.fields.String()
    rating = marshmallow.fields.String(validate=marshmallow.validate.OneOf(schemas.epc_rating_options))
    date = marshmallow.fields.Date()


class FeedbackSchema(marshmallow.Schema):
    session_id = marshmallow.fields.UUID(allow_none=True)
    page_name = marshmallow.fields.String(allow_none=True)
    data = marshmallow.fields.Raw()


class SuccessSchema(marshmallow.Schema):
    success = marshmallow.fields.Boolean()


def get_addresses_from_api(postcode):
    max_results_number = 100
    offset = 0

    json_response = OSApi(settings.OS_API_KEY).get_by_postcode(postcode, offset, max_results_number)
    if not json_response:
        return []

    total_results_number = json_response["header"]["totalresults"]
    if total_results_number == 0:
        return []
    api_results = json_response["results"]
    api_results_all = api_results

    # We have a max result number (in this case 100) for each call.
    # If we expect more than 100 results in total, we set the offset to 100 and request another 100 results.
    # Repeat until all results are requested and return a full list of results.
    if max_results_number < total_results_number:
        requested_results_number = max_results_number
        while requested_results_number < total_results_number:
            offset = requested_results_number

            json_response = OSApi(settings.OS_API_KEY).get_by_postcode(postcode, offset, max_results_number)
            if not json_response:
                return []

            api_results = json_response["results"]
            api_results_all.extend(api_results)

            requested_results_number += max_results_number

    return api_results_all


class SupplierConverter:
    def __init__(self, session_id):
        self.session_id = session_id

    def _get_supplier(self):
        return api.session.get_answer(self.session_id, "supplier")["supplier"]

    def _is_bulb(self):
        return self._get_supplier() == "Bulb, now part of Octopus Energy"

    def _is_utility_warehouse(self):
        return self._get_supplier() == "Utility Warehouse"

    def _is_shell(self):
        return self._get_supplier() == "Shell"

    def get_supplier_on_general_pages(self):
        supplier = self._get_supplier()
        if self._is_bulb():
            return supplier + ", "
        return supplier

    def get_supplier_on_success_page(self):
        supplier = self._get_supplier()
        if self._is_bulb() or self._is_shell():
            return "Octopus Energy"
        if self._is_utility_warehouse():
            return "E.ON Next"
        return supplier

    def replace_in_session_data(self, session_data):
        if self._is_bulb() or self._is_shell():
            session_data["supplier"] = "Octopus Energy"
        if self._is_utility_warehouse():
            session_data["supplier"] = "E.ON Next"
        return session_data


class Session(Entity):
    @with_schema(load=SaveAnswerSchema, dump=schemas.SessionSchema)
    @register_event(models.Event, "Answer saved")
    def save_answer(self, session_id, page_name, data):
        answer = models.Answer.objects.create(
            session_id=session_id,
            page_name=page_name,
            data=data,
        )
        return answer.data

    @with_schema(load=GetAnswerSchema, dump=schemas.SessionSchema)
    def get_answer(self, session_id, page_name):
        try:
            answer = models.Answer.objects.filter(session_id=session_id, page_name=page_name).latest("created_at")
            return answer.data
        except models.Answer.DoesNotExist:
            return {}

    @with_schema(load=GetPageAnswersSchema, dump=schemas.SessionSchema)
    def get_page_answers(self, session_id, page_name):
        page_answers = (
            models.Answer.objects.filter(session_id=session_id, page_name=page_name).order_by("created_at").all()
        )
        answers = {k: v for a in page_answers for (k, v) in a.data.items()}
        return answers

    @with_schema(load=GetSessionSchema, dump=schemas.SessionSchema)
    def get_session(self, session_id):
        answers = models.Answer.objects.filter(session_id=session_id).order_by("created_at").all()
        session = {k: v for a in answers for (k, v) in a.data.items()}
        return session

    @with_schema(load=CreateReferralSchema, dump=ReferralSchema)
    @register_event(models.Event, "Referral created")
    def create_referral(self, session_id):
        # add some cosmetic information to the exported referral to help out suppliers
        # e.g. set dependent answers that would be blank to a meaningful string

        answers = api.session.get_session(session_id)

        # filter to only answers given on the user's journey
        journey = calculate_journey(answers, confirm_and_submit_page)
        given_answers = {}
        for journey_page_name in journey:
            page_answers = api.session.get_page_answers(session_id, journey_page_name)
            given_answers = {**given_answers, **page_answers}

        # override property type of park home
        park_home_main_residence = given_answers.get(park_home_main_residence_field)
        if park_home_main_residence == field_yes:
            given_answers[property_type_field] = property_type_field_park_home
            given_answers[property_subtype_field] = property_type_field_park_home

        # override loft access if no loft
        loft = given_answers.get(loft_field)
        if loft == loft_field_no:
            given_answers[loft_access_field] = loft_access_field_no_loft
            given_answers[loft_insulation_field] = loft_insulation_field_no_loft

        # Users are given the option to select "no insulation" to improve question usability
        # This and "below threshold" are functionally identical from the supplier point of view.
        # They will be combined before the suppliers see it to improve supplier usability
        loft_insulation = given_answers.get(loft_insulation_field)
        if loft_insulation == given_answers.get(loft_insulation_field_no_insulation):
            given_answers[loft_insulation_field] = loft_insulation_field_less_than_threshold

        # ensure not found EPCs are displayed as such
        # this will normally be set as an answer on pressing submit on 'address' page
        # though this is not guaranteed, ie if user presses to enter manually
        # so this check ensures it's not missed out
        if epc_rating_field not in given_answers:
            given_answers[epc_rating_field] = epc_rating_field_not_found
            given_answers[epc_accept_suggested_epc_field] = epc_accept_suggested_epc_field_not_found

        # if the supplier has been replaced (e.g. Octopus manages Shell), then replace the Shell with Octopus in answers
        given_answers = SupplierConverter(session_id).replace_in_session_data(given_answers)

        supplier = portal.models.Supplier.objects.get(name=given_answers[supplier_field])
        referral = portal.models.Referral.objects.create(session_id=session_id, data=given_answers, supplier=supplier)
        referral_data = {"id": referral.id, "session_id": referral.session_id, "data": referral.data}
        return referral_data


class Address(Entity):
    @with_schema(load=FindAddressesSchema, dump=AddressSchema(many=True))
    def find_addresses(self, building_name_or_number, postcode):
        api_results = get_addresses_from_api(postcode=postcode)

        lpi_data = tuple(
            {"LPI": r["LPI"]}
            for r in api_results
            if r.get("LPI") is not None and self.is_current_residential(r.get("LPI"))
        )

        lpi_addresses = tuple(self.parse_lpi_to_address(r.get("LPI")) for r in lpi_data)

        uprns_to_use = tuple(address["uprn"] for address in lpi_addresses)

        dpa_data = tuple(
            {"DPA": r["DPA"]} for r in api_results if r.get("DPA") is not None and r.get("DPA")["UPRN"] in uprns_to_use
        )

        dpa_addresses = tuple(self.parse_dpa_to_address(r.get("DPA")) for r in dpa_data)

        dpa_uprns = tuple(address["uprn"] for address in dpa_addresses)

        joined_addresses = dpa_addresses + tuple(
            address for address in lpi_addresses if address["uprn"] not in dpa_uprns
        )

        if building_name_or_number:
            joined_addresses = tuple(
                [
                    a
                    for a in joined_addresses
                    if building_name_or_number.lower() in a["address_line_1"].lower()
                    or building_name_or_number.lower() in a["address_line_2"].lower()
                ]
            )

        return joined_addresses[:10]

    @with_schema(load=GetAddressSchema, dump=FullAddressSchema)
    def get_address(self, uprn):
        logger = logging.getLogger(__name__)
        api_keys = ast.literal_eval(settings.OS_API_KEY)
        for index, key in enumerate(api_keys):
            try:
                api = osdatahub.PlacesAPI(key)
            except requests.exceptions.HTTPError or requests.exceptions.RequestException as e:
                status_code = e.response.status_code
                if status_code == HTTPStatus.TOO_MANY_REQUESTS:
                    logger.error(f"The OS API usage limit has been hit for API key at index {index}.")
                    if index == len(api_keys) - 1:
                        logger.error("The OS API usage limit has been hit for all API keys")
                        raise ThrottledApiException
                    else:
                        continue

                logger.exception("An error occurred while attempting to fetch addresses.")
                break

        try:
            api_results = api.uprn(int(uprn), dataset="LPI")["features"]
            address = api_results[0]["properties"]["ADDRESS"]
            result = {"uprn": uprn, "address": address}
            return result
        except requests.exceptions.HTTPError or requests.exceptions.RequestException as e:
            if e.response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
                raise ThrottledApiException
            else:
                raise e

    def is_current_residential(self, lpi):
        return (
            lpi["POSTAL_ADDRESS_CODE"] != "N"  # is a postal address
            and lpi["LPI_LOGICAL_STATUS_CODE"] == "1"  # only want current addresses
            and lpi["CLASSIFICATION_CODE"].startswith("R")  # Residential addresses
            or lpi["CLASSIFICATION_CODE"].startswith("CE")  # Educational addresses
            or lpi["CLASSIFICATION_CODE"].startswith("X")  # Dual-use (residential and commercial) addresses
            or lpi["CLASSIFICATION_CODE"].startswith("M")  # Military addresses
        )

    def parse_lpi_to_address(self, lpi):
        line_1_parts = []
        line_2_parts = []

        sao_parts = []
        pao_parts = []

        # Organisation name
        if "ORGANISATION" in lpi:
            line_1_parts.append(lpi["ORGANISATION"].title())

        # SAO
        if "SAO_TEXT" in lpi:
            sao_parts.append(lpi["SAO_TEXT"].title())

        sao_start = ""
        if "SAO_START_NUMBER" in lpi:
            sao_start += lpi["SAO_START_NUMBER"]
        if "SAO_START_SUFFIX" in lpi:
            sao_start += lpi["SAO_START_SUFFIX"]

        sao_end = ""
        if "SAO_END_NUMBER" in lpi:
            sao_end += lpi["SAO_END_NUMBER"]
        if "SAO_END_SUFFIX" in lpi:
            sao_end += lpi["SAO_END_SUFFIX"]

        sao_numbers = ""
        if sao_start != "":
            sao_numbers += sao_start
        if sao_end != "":
            sao_numbers += "–" + sao_end
            # Use an en dash (–) for ranges

        if sao_numbers is not None:
            sao_parts.append(sao_numbers)

        if any(sao_parts):
            line_1_parts.extend(sao_parts)

        # PAO text goes on the line before the rest of the PAO, if present
        if "PAO_TEXT" in lpi:
            line_1_parts.append(lpi["PAO_TEXT"].title())

        # Rest of PAO
        pao_start = ""
        if "PAO_START_NUMBER" in lpi:
            pao_start += lpi["PAO_START_NUMBER"]
        if "PAO_START_SUFFIX" in lpi:
            pao_start += lpi["PAO_START_SUFFIX"]

        pao_end = ""
        if "PAO_END_NUMBER" in lpi:
            pao_end += lpi["PAO_END_NUMBER"]
        if "PAO_END_SUFFIX" in lpi:
            pao_end += lpi["PAO_END_SUFFIX"]

        pao_numbers = ""
        if pao_start != "":
            pao_numbers += pao_start
        if pao_end != "":
            pao_numbers += "–" + pao_end
            # Use an en dash (–) for ranges
        if pao_numbers != "":
            pao_parts.append(pao_numbers)

        if any(line_1_parts):
            line_2_parts.extend(pao_parts)
            if "STREET_DESCRIPTION" in lpi:
                line_2_parts.append(lpi["STREET_DESCRIPTION"].title())
        else:
            line_1_parts.extend(pao_parts)
            if "STREET_DESCRIPTION" in lpi:
                line_1_parts.append(lpi["STREET_DESCRIPTION"].title())

        line1 = ", ".join(line for line in line_1_parts if line)
        line2 = ", ".join(line for line in line_2_parts if line)

        address = {
            "address_line_1": line1,
            "address_line_2": line2,
            "town": lpi["TOWN_NAME"].title(),
            "postcode": lpi["POSTCODE_LOCATOR"],
            "local_custodian_code": lpi["LOCAL_CUSTODIAN_CODE"],
            "uprn": lpi["UPRN"],
        }

        return address

    def parse_dpa_to_address(self, dpa):
        line_1_parts = []

        if "DEPARTMENT_NAME" in dpa:
            line_1_parts.append(dpa["DEPARTMENT_NAME"].title())
        if "ORGANISATION_NAME" in dpa:
            line_1_parts.append(dpa["ORGANISATION_NAME"].title())
        if "SUB_BUILDING_NAME" in dpa:
            line_1_parts.append(dpa["SUB_BUILDING_NAME"].title())
        if "BUILDING_NAME" in dpa:
            line_1_parts.append(dpa["BUILDING_NAME"].title())
        if "BUILDING_NUMBER" in dpa:
            line_1_parts.append(dpa["BUILDING_NUMBER"])

        line_2_parts = []

        if "DOUBLE_DEPENDENT_LOCALITY" in dpa:
            line_1_parts.append(dpa["DOUBLE_DEPENDENT_LOCALITY"].title())
        if "DEPENDENT_LOCALITY" in dpa:
            line_1_parts.append(dpa["DEPENDENT_LOCALITY"].title())

        if "DEPENDENT_THOROUGHFARE_NAME" in dpa:
            line_1_parts.append(dpa["DEPENDENT_THOROUGHFARE_NAME"].title())
            if "THOROUGHFARE_NAME" in dpa:
                line_2_parts.insert(0, dpa["THOROUGHFARE_NAME"].title())
        else:
            if "THOROUGHFARE_NAME" in dpa:
                line_1_parts.append(dpa["THOROUGHFARE_NAME"].title())

        line1 = ", ".join(line for line in line_1_parts if line)
        line2 = ", ".join(line for line in line_2_parts if line)

        la_merges_dict = {
            "405": "440",
            "410": "440",
            "415": "440",
            "425": "440",
            "905": "940",
            "915": "940",
            "920": "940",
            "910": "935",
            "925": "935",
            "930": "935",
            "2705": "2745",
            "2710": "2745",
            "2715": "2745",
            "2720": "2745",
            "2725": "2745",
            "2730": "2745",
            "2735": "2745",
            "3305": "3300",
            "3310": "3300",
            "3325": "3300",
            "3330": "3300",
        }
        # Map:
        # Maps old custodian code onto new custodian code due to local authority merges
        #   405 - Aylesbury Vale, 410 - South Bucks, 415 - Chiltern, 425 - Wycombe
        #   to 440 - Buckinghamshire
        #   905 - Allerdale, 915 - Carlisle, 920 - Copeland
        #  to 940 - Cumberland
        #   910 - Barrow-in-Furness, 925 - Eden, 930 - South Lakeland
        #   to 935 - Westmorland and Furness

        #   2705 - Craven, 2710 - Hambleton, 2715 - Harrogate, 2720 - Richmondshire,
        #   2725 - Ryedale, 2730 - Scarborough, 2735 - Selby
        #   to 2745 - North Yorkshire

        # Map:
        #    3305 - Mendip, 3310 - Sedgemoor, 3325 - South Somerset, 3330 - Somerset West and Taunton
        #    to 3300 - Somerset

        custodian_code = ""
        if "LOCAL_CUSTODIAN_CODE" in dpa:
            custodian_code = la_merges_dict.get(dpa["LOCAL_CUSTODIAN_CODE"]) or dpa["LOCAL_CUSTODIAN_CODE"]

        address = {
            "address_line_1": line1,
            "address_line_2": line2,
            "town": dpa["POST_TOWN"].title(),
            "postcode": dpa["POSTCODE"],
            "local_custodian_code": custodian_code,
            "uprn": dpa["UPRN"],
        }

        return address


class EPC(Entity):
    @with_schema(load=GetScottishEPCSchema)
    def get_epc_scotland(self, uprn):
        try:
            epc = portal.models.ScottishEpcRating.objects.get(uprn=uprn)
        except portal.models.ScottishEpcRating.DoesNotExist:
            return {}

        improvements = epc.improvements
        alternative_improvements = epc.alternative_improvements
        all_improvements = improvements + (
            "|| Alternatives: " + alternative_improvements if alternative_improvements else ""
        )

        return {
            # follows column names in help_to_heat/frontdoor/mock_epc_api_data/sample_epc_response.json
            "uprn": epc.uprn,
            "current-energy-rating": epc.rating,
            "lodgement-date": epc.date,
            "property-type": epc.property_type,
            "address1": epc.address1,
            "address2": epc.address2,
            "address3": epc.address3,
            "postcode": epc.postcode,
            "building-reference-number": epc.building_reference_number,
            "potential-energy-rating": epc.potential_rating,
            "current-energy-efficiency": epc.current_energy_efficiency_rating,
            "potential-energy-efficiency": epc.potential_energy_efficiency_rating,
            "built-form": epc.built_form,
            "inspection-date": epc.inspection_date,
            "local-authority-label": epc.local_authority,
            "constituency-label": epc.constituency,
            "energy-consumption-current": epc.energy_consumption,
            "energy-consumption-potential": epc.potential_energy_consumption,
            "co2-emissions-current": epc.co2_emissions,
            "co2-emiss-curr-per-floor-area": epc.co2_emissions_per_floor_area,
            "co2-emissions-potential": epc.co2_emissions_potential,
            "total-floor-area": epc.floor_area,
            "floor-level": epc.floor_level,
            "floor-height": epc.floor_height,
            "energy-tariff": epc.energy_tariff,
            "mains-gas-flag": epc.mains_gas,
            "multi-glaze-proportion": epc.multiple_glazed_proportion,
            "extension-count": epc.extension_count,
            "number-habitable-rooms": epc.habitable_room_count,
            "number-heated-rooms": epc.heated_room_count,
            "floor-description": epc.floor_description,
            "floor-energy-eff": epc.floor_energy_efficiency,
            "windows-description": epc.windows_description,
            "walls-description": epc.wall_description,
            "walls-energy-eff": epc.wall_energy_efficiency,
            "walls-env-eff": epc.wall_environmental_efficiency,
            "mainheat-description": epc.main_heating_description,
            "mainheat-energy-eff": epc.main_heating_energy_efficiency,
            "mainheat-env-eff": epc.main_heating_environmental_efficiency,
            "main-fuel": epc.main_heating_fuel_type,
            "secondheat-description": epc.second_heating_description,
            "sheating-energy-eff": epc.second_heating_energy_efficiency,
            "roof-description": epc.roof_description,
            "roof-energy-eff": epc.roof_energy_efficiency,
            "roof-env-eff": epc.roof_environmental_efficiency,
            "lighting-description": epc.lighting_description,
            "lighting-energy-eff": epc.lighting_energy_efficiency,
            "lighting-env-eff": epc.lighting_environmental_efficiency,
            "mechanical-ventilation": epc.mechanical_ventilation,
            "construction-age-band": epc.construction_age_band,
            "tenure": epc.tenure,
            "improvements": all_improvements,
        }

    def get_address_and_epc_lmk(self, building_name_or_number, postcode):
        epc_api = EPCApi()
        data = epc_api.search_epc_details(building_name_or_number, postcode)
        address_and_epc_details = data["rows"]
        return address_and_epc_details

    def get_epc(self, lmk):
        epc_api = EPCApi()
        epc_details = epc_api.get_epc_details(lmk)
        epc_recommendations = epc_api.get_epc_recommendations(lmk)
        return epc_details, epc_recommendations


class Feedback(Entity):
    @with_schema(load=FeedbackSchema, dump=SuccessSchema)
    def save_feedback(self, session_id, page_name, data):
        models.Feedback.objects.create(session_id=session_id, page_name=page_name, data=data)
        return {"success": True}


api = Interface(session=Session(), address=Address(), epc=EPC(), feedback=Feedback())
