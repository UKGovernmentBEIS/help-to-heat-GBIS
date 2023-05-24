import marshmallow
from help_to_heat import portal
from help_to_heat.utils import Entity, Interface, register_event, with_schema

from . import models, schemas


class SaveAnswerSchema(marshmallow.Schema):
    session_id = marshmallow.fields.UUID()
    page_name = marshmallow.fields.String(validate=marshmallow.validate.OneOf(schemas.pages))
    data = marshmallow.fields.Nested(schemas.SessionSchema(unknown=marshmallow.EXCLUDE))


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


class Session(Entity):
    @with_schema(load=SaveAnswerSchema, dump=schemas.SessionSchema)
    @register_event(models.Event, "Answer saved")
    def save_answer(self, session_id, page_name, data):
        answer, created = models.Answer.objects.update_or_create(
            session_id=session_id,
            page_name=page_name,
            defaults={"data": data},
        )
        return answer.data

    @with_schema(load=GetAnswerSchema, dump=schemas.SessionSchema)
    def get_answer(self, session_id, page_name):
        try:
            answer = models.Answer.objects.get(session_id=session_id, page_name=page_name)
            return answer.data
        except models.Answer.DoesNotExist:
            return {}

    @with_schema(load=GetSessionSchema, dump=schemas.SessionSchema)
    def get_session(self, session_id):
        answers = models.Answer.objects.filter(session_id=session_id).all()
        session = {k: v for a in answers for (k, v) in a.data.items()}
        return session

    @with_schema(load=CreateReferralSchema, dump=ReferralSchema)
    @register_event(models.Event, "Referral created")
    def create_referral(self, session_id):
        answers = models.Answer.objects.filter(session_id=session_id).all()
        data = {k: v for a in answers for (k, v) in a.data.items()}
        supplier = portal.models.Supplier.objects.get(name=data["supplier"])
        referral = portal.models.Referral.objects.create(session_id=session_id, data=data, supplier=supplier)
        referral_data = {"id": referral.id, "session_id": referral.session_id, "data": referral.data}
        return referral_data


api = Interface(session=Session())