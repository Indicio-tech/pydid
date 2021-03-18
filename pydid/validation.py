"""Validation tools and helpers."""

from functools import wraps
from typing import Any

import voluptuous
from voluptuous import Invalid, MultipleInvalid, Required, ALLOW_EXTRA


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

    def __init__(self, required=None, extra=None):
        self.validator = {}
        self.serializer = {}
        self.deserializer = {}
        self.names = set()
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
            prop = func.__name__
            self.names.add(prop)

            key = data_key or prop
            key = Required(key) if required else key
            self.validator[key] = validate or object
            if key:
                self.serializer[Into(prop, key)] = serialize or validate or object
                self.deserializer[Into(key, prop)] = deserialize or validate or object
            else:
                self.serializer[key] = serialize or object
                self.deserializer[key] = deserialize or object
            return func

        return _add

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
