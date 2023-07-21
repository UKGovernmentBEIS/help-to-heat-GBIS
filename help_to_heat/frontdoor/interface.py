import marshmallow
import osdatahub
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
    text = marshmallow.fields.String()


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
    def find_addresses(self, text):
        api = osdatahub.PlacesAPI(settings.OS_API_KEY)
        api_results = api.find(text, dataset="LPI")["features"]
        if len(api_results) > 10:
            api_results = api_results[:10]
        results = tuple({"uprn": r["properties"]["UPRN"], "address": r["properties"]["ADDRESS"]} for r in api_results)
        return results

    @with_schema(load=GetAddressSchema, dump=AddressSchema)
    def get_address(self, uprn):
        api = osdatahub.PlacesAPI(settings.OS_API_KEY)
        api_results = api.uprn(int(uprn), dataset="LPI")["features"]
        address = api_results[0]["properties"]["ADDRESS"]
        result = {"uprn": uprn, "address": address}
        return result


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
