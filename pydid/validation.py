"""Validation tools and helpers."""

from functools import wraps

from voluptuous import Invalid, MultipleInvalid, validate


def validate_init(*s_args, **s_kwargs):
    """Wrapper around voluptuous.validate decorator for better errors."""

    def _validate_init(func):
        func = validate(*s_args, **s_kwargs)(func)

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


class As:
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
