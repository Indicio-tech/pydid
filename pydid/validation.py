"""Validation tools and helpers."""

from contextlib import contextmanager
from typing import Any, Callable, List, Type

from pydantic import ValidationError, root_validator, create_model


@contextmanager
def wrap_validation_error(error_to_raise: Type[Exception], message: str = None):
    """Wrap voluptuous erros with more friendly errors."""
    try:
        yield
    except ValidationError as error:
        raise error_to_raise(
            ":\n".join([message, str(error)]) if message else str(error)
        ) from error


def coerce(transformers: List[Callable]):
    """Apply transformations to data before parsing into model."""

    def _do_coercion(_model: Type, values: dict):
        for transformer in transformers:
            values = transformer(values)
        return values

    def _coerce(typ: Type[Any]):
        return create_model(
            typ.__name__,
            __module__=typ.__module__,
            __base__=typ,
            do_coercion=root_validator(pre=True, allow_reuse=True)(_do_coercion),
        )

    return _coerce
