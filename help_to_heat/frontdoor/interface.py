from typing import Dict, List
import marshmallow
import osdatahub
import requests
from django.conf import settings

from help_to_heat import portal
from help_to_heat.utils import Entity, Interface, register_event, with_schema

from . import models, schemas


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
    address = marshmallow.fields.String()


class GetEPCSchema(marshmallow.Schema):
    uprn = marshmallow.fields.Integer()


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
        data = self.get_session(session_id)
        supplier = portal.models.Supplier.objects.get(name=data["supplier"])
        referral = portal.models.Referral.objects.create(session_id=session_id, data=data, supplier=supplier)
        referral_data = {"id": referral.id, "session_id": referral.session_id, "data": referral.data}
        return referral_data


class Address(Entity):
    @with_schema(load=FindAddressesSchema, dump=AddressSchema(many=True))
    def find_addresses(self, building_name_or_number: str, postcode: str) -> List[Dict]:

        # api = osdatahub.PlacesAPI(settings.OS_API_KEY)
        # api_results = api.postcode(postcode, dataset=['LPI', 'DPA'], limit=200)["features"] or []

        url = f"https://api.os.uk/search/places/v1/postcode?maxresults=100&postcode={postcode}&lr=EN&dataset=DPA,LPI&key={settings.OS_API_KEY}"
        
        # if (offset is not null)
        # {
        #     path += $"&offset={offset}";
        # }
        
        # return new RequestParameters
        # {
        #     BaseAddress = config.BaseUrl,
        #     Path = path,
        #     Headers = new Dictionary<string, string> { { "Key", config.Key } }
        # };
        
        response = requests.get(url)
        json_response = response.json()
        api_results = json_response['results']
        lpi_data = tuple({"LPI": r["LPI"]} for r in api_results if r.get("LPI") is not None 
                    and self.is_current_residential(r.get("LPI")))
        
        lpi_addresses = tuple(self.parse_lpi_to_address(r.get("LPI")) for r in lpi_data)

        uprns_to_use = tuple(address["Uprn"] for address in lpi_addresses)

        dpa_data = tuple({"DPA": r["DPA"]} for r in api_results if r.get("DPA") is not None 
                    and r.get("DPA")["UPRN"] in uprns_to_use)
        
        dpa_addresses = tuple(self.parse_dpa_to_address(r.get("DPA")) for r in dpa_data)
        
        dpa_uprns = tuple(address["Uprn"] for address in dpa_addresses)
        
        # joined_addresses = list(dpa_addresses).extend([address for address in lpi_addresses if address["Uprn"] not in dpa_uprns])

        # var joinedAddresses = dpaAddresses.Concat(lpiAddresses.Where(la => !dpaUprns.Contains(la.Uprn))).ToList();

        
#             var filteredResults = buildingNameOrNumber is null
#                 ? joinedAddresses
#                 : joinedAddresses.Where(a =>
#                     a.AddressLine1.ToLower().Contains(buildingNameOrNumber.ToLower())
#                     || a.AddressLine2.ToLower().Contains(buildingNameOrNumber.ToLower()))
#                 .ToList();
        
        # if len(api_results) > 10:
        #     api_results = api_results[:10]
    
    @with_schema(load=GetAddressSchema, dump=AddressSchema)
    def get_address(self, uprn):
        api = osdatahub.PlacesAPI(settings.OS_API_KEY)
        api_results = api.uprn(int(uprn), dataset="LPI")["features"]
        address = api_results[0]["properties"]["ADDRESS"]
        result = {"uprn": uprn, "address": address}
        return result
    
    def is_current_residential(self, lpi):
        return (lpi["POSTAL_ADDRESS_CODE"] != "N" # is a postal address
                   and lpi["LPI_LOGICAL_STATUS_CODE"] == "1" # only want current addresses           
                   and lpi["CLASSIFICATION_CODE"].startswith("R") # Residential addresses
                   or lpi["CLASSIFICATION_CODE"].startswith("CE") # Educational addresses
                   or lpi["CLASSIFICATION_CODE"].startswith("X") # Dual-use (residential and commercial) addresses
                   or lpi["CLASSIFICATION_CODE"].startswith("M") # Military addresses
            )
    
    def parse_lpi_to_address(self, lpi):
        line_1_parts = []
        line2Parts = []
        
        saoParts = []
        paoParts = []

        # Organisation name
        if ("ORGANISATION" in lpi): line_1_parts.append(lpi["ORGANISATION"].title())
        
        # SAO
        if ("SAO_TEXT" in lpi): saoParts.append(lpi["SAO_TEXT"].title())

        saoStart = ""
        if ("SAO_START_NUMBER" in lpi): saoStart += lpi["SAO_START_NUMBER"]
        if ("SAO_START_SUFFIX" in lpi): saoStart += lpi["SAO_START_SUFFIX"]
        
        saoEnd = ""
        if ("SAO_END_NUMBER" in lpi): saoEnd += lpi["SAO_END_NUMBER"]
        if ("SAO_END_SUFFIX" in lpi): saoEnd += lpi["SAO_END_SUFFIX"]
        
        saoNumbers = ""
        if (saoStart != ""): saoNumbers += saoStart
        if (saoEnd != ""): saoNumbers += ("–" + saoEnd);  # Use an en dash (–) for ranges
        
        if (saoNumbers is not None): saoParts.append(saoNumbers)
        
        if (any(saoParts)): line_1_parts.extend(saoParts)

        # PAO text goes on the line before the rest of the PAO, if present
        if ("PAO_TEXT" in lpi): line_1_parts.append(lpi["PAO_TEXT"].title())

        # Rest of PAO
        paoStart = ""
        if ("PAO_START_NUMBER" in lpi): paoStart += lpi["PAO_START_NUMBER"]
        if ("PAO_START_SUFFIX" in lpi): paoStart += lpi["PAO_START_SUFFIX"]
        
        paoEnd = ""
        if ("PAO_END_NUMBER" in lpi): paoEnd += lpi["PAO_END_NUMBER"]
        if ("PAO_END_SUFFIX" in lpi): paoEnd += lpi["PAO_END_SUFFIX"]
        
        paoNumbers = ""
        if (paoStart != ""): paoNumbers += paoStart
        if (paoEnd != ""): paoNumbers += ("–" + paoEnd);  # Use an en dash (–) for ranges
        if (paoNumbers != ""): paoParts.append(paoNumbers)
        
        if (any(line_1_parts)):
            line2Parts.extend(paoParts)
            if ("STREET_DESCRIPTION" in lpi): line2Parts.append(lpi["STREET_DESCRIPTION"].title())
        else:
            line_1_parts.extend(paoParts)
            if ("STREET_DESCRIPTION" in lpi): line_1_parts.append(lpi["STREET_DESCRIPTION"].title())

        line1 = ", ".join(line_1_parts)
        line2 = ", ".join(line2Parts)
        
        address = {
            "AddressLine1": line1,
            "AddressLine2": line2,
            "Town": lpi["TOWN_NAME"].title(),
            "Postcode": lpi["POSTCODE_LOCATOR"],
            "LocalCustodianCode": lpi["LOCAL_CUSTODIAN_CODE"],
            "Uprn": lpi["UPRN"]
        }

        return address
    
    def parse_dpa_to_address(self, dpa):
        
        line_1_parts = []
        
        if ("DEPARTMENT_NAME" in dpa): line_1_parts.append(dpa["DEPARTMENT_NAME"].title())
        if ("ORGANISATION_NAME" in dpa): line_1_parts.append(dpa["ORGANISATION_NAME"].title())
        if ("SUB_BUILDING_NAME" in dpa): line_1_parts.append(dpa["SUB_BUILDING_NAME"].title())
        if ("BUILDING_NAME" in dpa): line_1_parts.append(dpa["BUILDING_NAME"].title())
        if ("BUILDING_NUMBER" in dpa): line_1_parts.append(dpa["BUILDING_NUMBER"])

        line2Parts = []
        
        if ("DOUBLE_DEPENDENT_LOCALITY" in dpa): line_1_parts.append(dpa["DOUBLE_DEPENDENT_LOCALITY"].title())
        if ("DEPENDENT_LOCALITY" in dpa): line_1_parts.append(dpa["DEPENDENT_LOCALITY"].title())

        if ("DEPENDENT_THOROUGHFARE_NAME" and "THOROUGHFARE_NAME" in dpa): line_1_parts.append(dpa["THOROUGHFARE_NAME"].title())
        else:
           line_1_parts.append(dpa["DEPENDENT_THOROUGHFARE_NAME"].title())
           line2Parts.insert(0, dpa["THOROUGHFARE_NAME"].title())

        line1 = ", ".join(line_1_parts)
        line2 = ", ".join(line2Parts)

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
        #   405 - Aylesbury Vale, 410 - South Bucks, 415 - Chiltern, 425 - Wycombe
        #   to 440 - Buckinghamshire
        #   905 - Allerdale, 915 - Carlisle, 920 - Copeland  
        #  to 940 - Cumberland
        #   910 - Barrow-in-Furness, 925 - Eden, 930 - South Lakeland
        #   to 935 - Westmorland and Furness

        #   2705 - Craven, 2710 - Hambleton, 2715 - Harrogate, 2720 - Richmondshire, 2725 - Ryedale, 2730 - Scarborough, 2735 - Selby
        #   to 2745 - North Yorkshire   
        
        # Map:
        #    3305 - Mendip, 3310 - Sedgemoor, 3325 - South Somerset, 3330 - Somerset West and Taunton
        #    to 3300 - Somerset

        custodianCode = ""
        if ("LOCAL_CUSTODIAN_CODE" in dpa): custodianCode = la_merges_dict.get(dpa["LOCAL_CUSTODIAN_CODE"]) or dpa["LOCAL_CUSTODIAN_CODE"]

        address = {
            "AddressLine1": line1,
            "AddressLine2": line2,
            "Town": dpa["POST_TOWN"].title(),
            "Postcode": dpa["POST_TOWN"],
            "LocalCustodianCode": custodianCode,
            "Uprn": dpa["UPRN"]
        }

        return address
    
    
class EPC(Entity):
    @with_schema(load=GetEPCSchema, dump=EPCSchema)
    def get_epc(self, uprn):
        try:
            epc = portal.models.EpcRating.objects.get(uprn=uprn)
        except portal.models.EpcRating.DoesNotExist:
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
