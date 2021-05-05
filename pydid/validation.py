"""Validation tools and helpers."""

from contextlib import contextmanager
from typing import Any, Callable, List, Set, Type

from pydantic import ValidationError, root_validator, create_model


@contextmanager
def wrap_validation_error(error_to_raise: Type[Exception], message: str = None):
    """Wrap validation erros with more friendly errors."""
    try:
        yield
    except ValidationError as error:
        raise error_to_raise(
            ":\n".join([message, str(error)]) if message else str(error)
        ) from error


def validator(transformers: List[Callable]):
    """Transform or validate data before parsing into model."""

    def _do_validation(_model: Type, values: dict):
        for transformer in transformers:
            values = transformer(values)
        return values

    def _validation(typ: Type[Any]):
        return create_model(
            typ.__name__,
            __module__=typ.__module__,
            __base__=typ,
            do_coercion=root_validator(pre=True, allow_reuse=True)(_do_validation),
        )

    return _validation


coerce = validator


def required_group(props: Set[str]):
    """Require at least one of the properties to be present."""

    def _require_group(_model, values: dict):
        defined_props = props & {
            key for key, value in values.items() if value is not None
        }
        if len(defined_props) < 1:
            raise ValueError(
                "At least one of {} was required; none found".format(props)
            )
        return values

    return root_validator(allow_reuse=True)(_require_group)
