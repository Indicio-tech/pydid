"""Validation tools and helpers."""

from abc import ABCMeta, abstractclassmethod, abstractmethod
from collections import namedtuple
from contextlib import contextmanager
from enum import Enum, EnumMeta
from functools import wraps
from typing import Any, Iterable, Set, Type

import voluptuous
from voluptuous import ALLOW_EXTRA, Invalid, MultipleInvalid, Required, Schema


def validate_init(*s_args, **s_kwargs):
    """Wrapper around voluptuous.validate decorator for better errors."""

    def _validate_init(func):
        func = voluptuous.validate(*s_args, **s_kwargs)(func)

        @wraps(func)
        def _wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except MultipleInvalid as err:
                raise ValueError(
                    "Invalid argument for {}:\n\t{}".format(
                        func.__qualname__,
                        "\n\t".join(
                            [
                                "{}: {}".format(error.path, Exception.__str__(error))
                                for error in err.errors
                            ]
                        ),
                    )
                ) from err

        return _wrapper

    return _validate_init


@contextmanager
def wrap_validation_error(error_to_raise: Type[Exception], message: str = None):
    """Wrap voluptuous erros with more friendly errors."""
    try:
        yield
    except MultipleInvalid as error:
        raise error_to_raise(
            "{}:\n\t{}".format(
                message or "Validation error",
                "\n\t".join([str(sub_error) for sub_error in error.errors]),
            )
        ) from error


class Into:
    """Validator that always returns a given value."""

    def __init__(self, from_value, to_value):
        self.from_value = from_value
        self.to_value = to_value

    def __call__(self, value):
        """Validate."""
        if value != self.from_value:
            raise Invalid("{} does not match {}".format(value, self.from_value))
        return self.to_value


def unwrap_if_list_of_one(value):
    """Unwrap a value froma list if list is length one."""
    if value and len(value) == 1:
        return value[0]
    return value


def single_to_list(value):
    """Wrap value in list if not already."""
    if isinstance(value, list):
        return value
    return [value]


def serialize(value):
    """Call serialize on passed value."""
    return value.serialize()


class Properties:
    """Aggregator of property info for use in validation and serialization."""

    Property = namedtuple(
        "Property",
        ["name", "data_key", "required", "validate", "serialize", "deserialize"],
    )

    def __init__(self, required=None, extra=None):
        self.validator = {}
        self.serializer = {}
        self.deserializer = {}
        self.props = []
        self.extra = extra
        self.required = required

    def add(
        self,
        *,
        data_key: str = None,
        required: bool = False,
        validate: Any = None,
        serialize: Any = None,
        deserialize: Any = None
    ):
        """Decorator defining field information."""

        def _add(func):
            prop = self.Property(
                func.__name__,
                data_key,
                required,
                validate or object,
                serialize or validate or object,
                deserialize or validate or object,
            )
            self.props.append(prop)

            key = data_key or prop.name
            key = Required(key) if required else key
            self.validator[key] = prop.validate
            if data_key:
                self.serializer[Into(prop.name, data_key)] = prop.serialize
                self.deserializer[Into(data_key, prop.name)] = prop.deserialize
            else:
                self.serializer[key] = prop.serialize
                self.deserializer[key] = prop.deserialize
            return func

        return _add

    @property
    def names(self):
        """Return names of properties."""
        return [prop.name for prop in self.props]

    def validate(self, value):
        """Validate properties from value."""
        return voluptuous.Schema(
            self.validator,
            required=self.required,
            extra=self.extra or voluptuous.PREVENT_EXTRA,
        )(value)

    def serialize(self, value):
        """Serialize properties."""
        return voluptuous.Schema(self.serializer, extra=ALLOW_EXTRA)(
            {
                name: getattr(value, name)
                for name in self.names
                if getattr(value, name) is not None
            }
        )

    def deserialize(self, value):
        """Deserialize properties."""
        return voluptuous.Schema(self.deserializer, extra=ALLOW_EXTRA)(value)


class ABCEnumMeta(EnumMeta, ABCMeta):
    """Metaclass combo for Enum ABCs."""


class Option(Enum, metaclass=ABCEnumMeta):
    """Base class for serialization and validation options."""

    @property
    @abstractmethod
    def priority(self) -> int:
        """Define options application priority."""

    @property
    @abstractmethod
    def schema(self) -> Schema:
        """Define schema applied for option."""

    @abstractclassmethod
    def apply(cls, value: dict, options: Set["Option"]) -> dict:
        """Apply options to value."""

    @staticmethod
    def schemas_in_application_order(options: Set["Option"]) -> Iterable[Schema]:
        """Return schemas of options in the order they should be applied."""
        return map(
            lambda option: option.schema,
            sorted(options, key=lambda option: option.priority),
        )
