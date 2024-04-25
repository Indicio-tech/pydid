"""Validation tools and helpers."""

from contextlib import contextmanager
from typing import Set, Type

from pydantic import ValidationError, ValidationInfo, model_validator


@contextmanager
def wrap_validation_error(error_to_raise: Type[Exception], message: str = None):
    """Wrap validation errors with more friendly errors."""
    try:
        yield
    except ValidationError as error:
        raise error_to_raise(
            ":\n".join([message, str(error)]) if message else str(error)
        ) from error


def required_group(props: Set[str]):
    """Require at least one of the properties to be present."""

    def _require_group(_model, _: ValidationInfo):
        if not isinstance(_model, dict):
            _model = _model.__dict__

        defined_props = props & {
            key for key, value in _model.items() if value is not None
        }
        if len(defined_props) < 1:
            raise ValueError(
                "At least one of {} was required; none found".format(props)
            )
        return _model

    return model_validator(mode="after")(_require_group)
