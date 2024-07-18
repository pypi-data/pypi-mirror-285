from contextlib import contextmanager
from datetime import datetime
import logging
from typing import ClassVar, Dict, List, Optional

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, validate_model
from pydantic.main import object_setattr
from pytz import UTC

from chaiverse.secrets import scrub_secrets
from chaiverse.database import _FirebaseDatabase


class class_property(property):
    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)


class InfernoLogEntry(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    entry: str
    level: str
    line_number: int
    path: str

    @staticmethod
    def from_logging_record(record: logging.LogRecord):
        entry = scrub_secrets(record.msg)
        log_entry = InfernoLogEntry(
            timestamp=datetime.utcfromtimestamp(record.created).replace(tzinfo=UTC),
            entry=entry,
            level=record.levelname,
            line_number=record.lineno,
            path=record.pathname
        )
        return log_entry


class InfernoModel(BaseModel):
    """
    Inferno is a light-weight object relational-mapper (ORM/ODM)
    for Firebase. It maps records in the database to python
    objects to ensure type-safety, validation and encourage
    cleaner coding standards when interfacing with the database.
    """
    database: ClassVar[_FirebaseDatabase]
    path: ClassVar[str]

    logs: Optional[List[InfernoLogEntry]]

    @class_property
    def lazy(cls):
        # Mixin lazy behaviour into base class
        lazy_class = type(f"Lazy{cls.__name__}", (LazyInfernoModelMixin, cls), {})
        return lazy_class

    @classmethod
    def create(cls, **kwargs):
        data = cls(**kwargs)
        msg = f'entry with id "{data.id}" already exists in database! Please use a different id'
        assert not cls.is_in_database(**{cls._id: data.id}), msg
        return data

    @classmethod
    def from_id(cls, default=None, **kwargs):
        instance_id = cls._get_instance_id(kwargs)
        data = cls.database.get(path=f'{cls.path}/{instance_id}') or default
        assert data is not None, f'no entry with id "{instance_id}" found on database!'
        return cls(**data)

    @classmethod
    def where(cls, **kwargs):
        records = cls.database.where(path=cls.path, **kwargs)
        return [cls(**data) for data in records]

    @classmethod
    def all(cls, **kwargs):
        all_entries = cls.database.get(path=cls.path)
        all_records = all_entries.values() if all_entries else []
        return [cls(**data) for data in all_records]

    @classmethod
    def paginate(cls, index, limit):
        # Paginate (in reverse order) an Inferno model with a sortable id
        entries = cls.database.query_by_child_value_range(cls.path, cls._id, end_at=index, limit_to_last=limit)
        entries = [cls(**entry) for entry in entries.values()] if entries else []
        entries.sort(key=lambda x: getattr(x, cls._id), reverse=True)
        return entries

    @classmethod
    def is_in_database(cls, **kwargs):
        instance_id = cls._get_instance_id(kwargs)
        is_in = cls.database.is_in_database(path=f'{cls.path}/{instance_id}')
        return is_in

    def to_dict(self, **kwargs):
        serialised_record = jsonable_encoder(self, **kwargs)
        return serialised_record

    def to_lazy(self):
        kwargs = {self.__class__._id: self.id}
        lazy_model = self.lazy.from_id(**kwargs)
        return lazy_model

    @contextmanager
    def register_logger(self):
        handler = InfernoLoggerHandler(inferno_model=self, level=logging.DEBUG)
        try:
            root_logger = logging.getLogger()
            root_logger.addHandler(handler)
            yield
        finally:
            root_logger.removeHandler(handler)

    def save(self):
        record = self._build_save_record()
        self.database.multi_update(path="/", record=record)

    def dict(self, *args, **kwargs):
        # So that FastAPI doesn't include null values in response
        kwargs["exclude_none"] = True
        return BaseModel.dict(self, *args, **kwargs)

    @property
    def id(self):
        id_field = self.__class__._id
        instance_id = getattr(self, id_field)
        return instance_id

    @classmethod
    def _get_denormalised_fields(cls):
        # Cannot set this as a Pydantic ClassVar as it gets shared across all
        # InfernoModel instances
        denormalised_fields = getattr(cls, "_denormalised_fields", {})
        return denormalised_fields

    @classmethod
    def _get_instance_id(cls, kwargs):
        assert cls._id in kwargs, f'invalid keyword id, please use keyword "{cls._id}"'
        instance_id = kwargs[cls._id]
        return instance_id

    def _build_save_record(self):
        record = {self.path: {self.id: self.to_dict()}}
        for field, path in self._get_denormalised_fields().items():
            denormalised_record = {path: {self.id: self.to_dict(include=[self._id, field])}}
            record.update(denormalised_record)
        return record


class LazyInfernoModelMixin():

    @classmethod
    def construct(cls, **kwargs):
        # Build pydantic model without validation
        instance = cls.__new__(cls)
        # Initialize pydantic private attributes
        object_setattr(instance, '__fields_set__', set())
        instance._init_private_attributes()
        for field, value in kwargs.items():
            instance._set_field(field, value)
        return instance

    @classmethod
    def from_id(cls, **kwargs):
        assert cls._id in kwargs, f'invalid keyword id, please use keyword "{cls._id}"'
        instance = cls.construct()
        instance_id = kwargs[cls._id]
        instance._set_field(cls._id, instance_id)
        return instance

    @classmethod
    def where(cls, **kwargs):
        assert len(kwargs) == 1, "Cannot perform a lazy where on more than one field!"
        field = list(kwargs.keys())[0]
        assert field in cls._get_denormalised_fields(), f"Cannot perform a lazy where on the field `{field}` as it has not been denormalised!"
        denormalised_path = cls._denormalised_fields[field]
        records = cls.database.where(path=denormalised_path, **kwargs)
        return [cls.construct(**data) for data in records]

    def _set_field(self, field, value):
        data = {field: value}
        values, _, validation_error = validate_model(self.__class__, data)
        if field not in values.keys():
            validation_error = _get_pydantic_errors_for_field(validation_error, field)
            raise validation_error
        object_setattr(self, field, value)

    def __getattribute__(self, field):
        value = super().__getattribute__(field)
        # Have to redirect to database if None as optional fields are
        # instantiated with None (and therefore have a value)
        if value is None and field in self.__fields__:
            value = self.__getattr__(field)
        return value

    def __getattr__(self, field):
        if field in self.__fields__:
            value = self.database.get(f"{self.path}/{self.id}/{field}")
            self._set_field(field, value)
        else:
            value = super().__getattribute__(field)
        return value


class InfernoLoggerHandler(logging.Handler):
    def __init__(self, inferno_model, level):
        super().__init__(level)
        # Convert to lazy to ensure we are not overwriting data in other
        # threads while logging
        self.inferno_model = inferno_model.to_lazy()

    def emit(self, record):
        log_entry = InfernoLogEntry.from_logging_record(record)
        if not self.inferno_model.logs:
            self.inferno_model.logs = []
        self.inferno_model.logs.append(log_entry)
        self.inferno_model.save()


def _get_pydantic_errors_for_field(validation_error, field):
    errors = [
        err_wrapper for err_wrapper in validation_error.raw_errors
        if err_wrapper.loc_tuple()[0] == field
    ]
    validation_error.raw_errors = errors
    return validation_error


def set_id(field: str):
    def wrapped(cls):
        cls._id = field
        return cls
    return wrapped


def denormalise_field(field: str, path_format: str = "{path}_{field}_denormalisation"):
    # Used to duplicate information in an Inferno model to improve read
    # performance, as is usually suggested when dealing with NoSQL databases
    # (especially Firebase)
    # See https://firebase.blog/posts/2013/04/denormalizing-your-data-is-normal
    def wrapped(cls):
        denormalisation_path = path_format.format(path=cls.path, field=field)
        cls._denormalised_fields = getattr(cls, "_denormalised_fields", {})
        cls._denormalised_fields[field] = denormalisation_path
        return cls
    return wrapped
