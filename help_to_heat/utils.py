import base64
import enum
import functools
import hashlib
import inspect
import secrets
import types
import uuid
import itertools
from datetime import datetime

import marshmallow
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db import models
from django.http import HttpResponseNotAllowed

event_names = set()


class ChoicesMeta(enum.EnumMeta):
    """A metaclass for creating a enum choices."""

    def __new__(metacls, classname, bases, classdict, **kwds):
        labels = []
        for key in classdict._member_names:
            value = classdict[key]
            if isinstance(value, (list, tuple)) and len(value) > 1 and isinstance(value[-1], str):
                value, label = value
            elif hasattr(value, "name"):
                label = str(value.name)
            else:
                label = value
                value = key
            labels.append(label)
            # Use dict.__setitem__() to suppress defenses against double
            # assignment in enum's classdict.
            dict.__setitem__(classdict, key, value)
        cls = super().__new__(metacls, classname, bases, classdict, **kwds)
        for member, label in zip(cls.__members__.values(), labels):
            member._label_ = label
        return enum.unique(cls)

    def __contains__(cls, member):
        if not isinstance(member, enum.Enum):
            # Allow non-enums to match against member values.
            return any(x.value == member for x in cls)
        return super().__contains__(member)

    @property
    def names(cls):
        return tuple(member.name for member in cls)

    @property
    def choices(cls):
        return tuple((member.name, member.label) for member in cls)

    @property
    def labels(cls):
        return tuple(label for _, label in cls.choices)

    @property
    def values(cls):
        return tuple(value for value, _ in cls.choices)

    @property
    def options(cls):
        return tuple({"value": value, "text": text} for value, text in cls.choices)


class Choices(enum.Enum, metaclass=ChoicesMeta):
    """Class for creating enumerated choices."""

    @types.DynamicClassAttribute
    def label(self):
        return self._label_

    def __repr__(self):
        return f"{self.__class__.__qualname__}.{self._name_}"

    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return super().__eq__(other)
        return self.value == other

    def __hash__(self):
        return hash(self._name_)


class MethodDispatcher:
    def __new__(cls, request, *args, **kwargs):
        view = super().__new__(cls)
        method_name = request.method.lower()
        method = getattr(view, method_name, None)
        if method:
            return method(request, *args, **kwargs)
        else:
            return HttpResponseNotAllowed(request)


class UUIDPrimaryKeyBase(models.Model):
    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(editable=False, auto_now_add=True)
    modified_at = models.DateTimeField(editable=False, auto_now=True)

    class Meta:
        abstract = True
        ordering = ["created_at"]


class DuplicateEvent(Exception):
    pass


def get_arguments(func, *args, **kwargs):
    """Calculate what the args would be inside a function"""
    sig = inspect.signature(func)
    bound_args = sig.bind(*args, **kwargs)
    bound_args.apply_defaults()
    arguments = bound_args.arguments
    return arguments


def _register_event(EventModel, event_name, arguments):  # noqa N803
    event_names.add(event_name)
    arguments = {key: value for (key, value) in arguments.items() if key != "self"}
    event = EventModel(name=event_name, data=arguments)
    event.save()


def resolve_schema(schema):
    """Allow either a class or an instance to be passed"""
    if isinstance(schema, marshmallow.schema.SchemaMeta):
        schema = schema()
    return schema


def register_event(EventModel, event_name):  # noqa N803
    def _decorator(func):
        func.event_name = event_name

        @functools.wraps(func)
        def _inner(*args, **kwargs):
            arguments = get_arguments(func, *args, **kwargs)
            _register_event(EventModel, event_name, arguments)
            return func(*args, **kwargs)

        return _inner

    return _decorator


def process_self(func, arguments):
    """Remove `self` from arguments and bind it to func"""
    if "self" in arguments:
        func = functools.partial(func, arguments["self"])
        arguments = {k: v for k, v in arguments.items() if k != "self"}
    return func, arguments


def apply_schema(schema, data, load_or_dump):
    """Apply a schema to some data"""
    if not schema:
        return data
    if load_or_dump not in ("load", "dump"):
        raise ValueError(f"Unknown value {load_or_dump}")
    if schema:
        schema = resolve_schema(schema)
        arguments = getattr(schema, load_or_dump)(data)
    return arguments


def with_schema(default=None, load=None, dump=None):
    """Applies the load_schema.load on the arguments to the function,
    and dump_schema.dump on the result of the function.

    This ensures that validation has been passed and that the result of the
    function is JSON serialisable"""
    load_schema = load or default
    dump_schema = dump or default

    def _decorator(func):
        @functools.wraps(func)
        def _inner(*args, **kwargs):
            arguments = get_arguments(func, *args, **kwargs)
            bound_func, arguments = process_self(func, arguments)
            arguments = apply_schema(load_schema, arguments, "load")
            result = bound_func(**arguments)
            result = apply_schema(dump_schema, result, "dump")
            return result

        return _inner

    return _decorator


class Interface:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

        all_event_names = tuple(
            event_name for entity in kwargs.values() for event_name in getattr(entity, "event_names", ())
        )
        if len(all_event_names) != len(set(all_event_names)):
            raise DuplicateEvent(all_event_names)
        self.event_names = all_event_names


class Entity:
    def __init__(self):
        possible_methods = (getattr(self, key) for key in dir(self) if not key.startswith("_"))
        possible_event_names = (getattr(item, "event_name", None) for item in possible_methods)
        self.event_names = tuple(item for item in possible_event_names if item)


def make_totp_key():
    return secrets.token_hex(32)


def make_totp_secret(user_id, key, length=32):
    raw = ":".join((str(user_id), key, settings.SECRET_KEY))
    raw_bytes = raw.encode("utf-8")
    hashed_bytes = hashlib.sha256(raw_bytes)
    digest = hashed_bytes.digest()
    encoded_secret = base64.b32encode(digest)
    summary = encoded_secret[:32].decode("ascii")
    return summary


def get_current_and_next_month_names(month_names):
    now = datetime.now()
    current_month = month_names[now.month - 1]
    next_month = month_names[(now + relativedelta(months=+1)).month - 1]
    return current_month, next_month


# Latest Quarter in current dump -> epc cutoff month, next expected dump month
# Q1 -> april, august
# Q2 -> july, november
# Q3 -> october, february
# Q4 -> january, may
# we update the month names manually on each scottish data dump
# this is to tell the user the first month we have no EPCs for, and the next month we expect to perform a dump
def get_current_scottish_epc_cutoff_and_next_dump_month_names(month_names):
    return month_names[9], month_names[1]


def get_most_recent_epc_per_uprn(address_and_lmk_details):
    most_recent_address_and_lmk_details = []
    address_and_lmk_details.sort(key=lambda x: x['uprn'], reverse=True)

    for _, group in itertools.groupby(address_and_lmk_details, lambda x: x['uprn']):
        item = max(list(group), key=lambda x: datetime.strptime(x['lodgement-date'], '%Y-%m-%d'))
        most_recent_address_and_lmk_details.append(item)

    return most_recent_address_and_lmk_details
