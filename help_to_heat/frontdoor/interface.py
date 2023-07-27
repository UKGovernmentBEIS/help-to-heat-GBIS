import marshmallow
import osdatahub
from django.conf import settings

from help_to_heat import portal
from help_to_heat.utils import Entity, Interface, register_event, with_schema

from . import models, schemas
from .os_api import OSApi


class SaveAnswerSchema(marshmallow.Schema):
    session_id = marshmallow.fields.UUID()
    page_name = marshmallow.fields.String(validate=marshmallow.validate.OneOf(schemas.pages))
    data = marshmallow.fields.Nested(schemas.SessionSchema(unknown=marshmallow.EXCLUDE))


class RemoveAnswerSchema(marshmallow.Schema):
    session_id = marshmallow.fields.UUID()
    page_name = marshmallow.fields.String(validate=marshmallow.validate.OneOf(schemas.pages))


class GetAnswerSchema(marshmallow.Schema):
    session_id = marshmallow.fields.UUID()
    page_name = marshmallow.fields.String(validate=marshmallow.validate.OneOf(schemas.pages))


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
    uprn = marshmallow.fields.Integer()


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


class GetEPCSchema(marshmallow.Schema):
    uprn = marshmallow.fields.Integer()
    country = marshmallow.fields.String()


class EPCSchema(marshmallow.Schema):
    uprn = marshmallow.fields.Integer()
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


class BulbSupplierConverter:
    def __init__(self, session_id):
        self.session_id = session_id

    def _get_supplier(self):
        return api.session.get_answer(self.session_id, "supplier")["supplier"]

    def _is_bulb(self):
        return self._get_supplier() == "Bulb, now part of Octopus Energy"

    def get_supplier_and_add_comma_after_bulb(self):
        supplier = self._get_supplier()
        if self._is_bulb():
            return supplier + ", "
        return supplier

    def get_supplier_and_replace_bulb_with_octopus(self):
        supplier = self._get_supplier()
        if self._is_bulb():
            return "Octopus"
        return supplier

    def replace_bulb_with_octopus_in_session_data(self, session_data):
        supplier = session_data["supplier"]
        if self._is_bulb():
            session_data["supplier"] = "Octopus"
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

    @with_schema(load=GetSessionSchema, dump=schemas.SessionSchema)
    def get_session(self, session_id):
        answers = models.Answer.objects.filter(session_id=session_id).order_by("created_at").all()
        session = {k: v for a in answers for (k, v) in a.data.items()}
        return session

    @with_schema(load=CreateReferralSchema, dump=ReferralSchema)
    @register_event(models.Event, "Referral created")
    def create_referral(self, session_id):
        session_data = api.session.get_session(session_id)
        data = BulbSupplierConverter(session_id).replace_bulb_with_octopus_in_session_data(session_data)
        supplier = portal.models.Supplier.objects.get(name=data["supplier"])
        referral = portal.models.Referral.objects.create(session_id=session_id, data=data, supplier=supplier)
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
        api = osdatahub.PlacesAPI(settings.OS_API_KEY)
        api_results = api.uprn(int(uprn), dataset="LPI")["features"]
        address = api_results[0]["properties"]["ADDRESS"]
        result = {"uprn": uprn, "address": address}
        return result

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

        if "DEPENDENT_THOROUGHFARE_NAME" and "THOROUGHFARE_NAME" in dpa:
            line_1_parts.append(dpa["THOROUGHFARE_NAME"].title())
        else:
            line_1_parts.append(dpa["DEPENDENT_THOROUGHFARE_NAME"].title())
            line_2_parts.insert(0, dpa["THOROUGHFARE_NAME"].title())

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
    @with_schema(load=GetEPCSchema, dump=EPCSchema)
    def get_epc(self, uprn, country):
        try:
            if country == "England" or country == "Wales":
                epc = portal.models.EpcRating.objects.get(uprn=uprn)
            elif country == "Scotland":
                epc = portal.models.ScottishEpcRating.objects.get(uprn=uprn)
            else:
                epc = None
        except (portal.models.EpcRating.DoesNotExist, portal.models.ScottishEpcRating.DoesNotExist):
            epc = None
        if epc:
            data = {"uprn": epc.uprn, "rating": epc.rating, "date": epc.date}
        else:
            data = {}
        return data


class Feedback(Entity):
    @with_schema(load=FeedbackSchema, dump=SuccessSchema)
    def save_feedback(self, session_id, page_name, data):
        models.Feedback.objects.create(session_id=session_id, page_name=page_name, data=data)
        return {"success": True}


api = Interface(session=Session(), address=Address(), epc=EPC(), feedback=Feedback())
