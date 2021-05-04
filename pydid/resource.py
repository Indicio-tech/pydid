"""Resource class that forms the base of all DID Document components."""

from typing import Any, Dict, Type, TypeVar

from inflection import camelize
from pydantic import BaseModel, Extra, parse_obj_as
from typing_extensions import Literal
import typing_extensions

from .validation import wrap_validation_error


ResourceType = TypeVar("ResourceType", bound="Resource")


if hasattr(typing_extensions, "get_args"):
    from typing_extensions import get_args, get_origin

    def get_literal_values(literal):
        """Return the args of a literal."""
        return get_args(literal)

    def is_literal(type_):
        """Return if type is literal."""
        return get_origin(type_) is Literal


else:
    # Python 3.6 and Literals behave differently
    from typing_extensions import _Literal

    def get_literal_values(literal):
        """Return the args of a literal."""
        return literal.__values__

    def is_literal(type_):
        """Return if type is literal."""
        return isinstance(type_, _Literal)


class Resource(BaseModel):
    """Base class for DID Document components."""

    class Config:
        """Configuration for Resources."""

        underscore_attrs_are_private = True
        extra = Extra.allow
        allow_population_by_field_name = True

        @classmethod
        def alias_generator(cls, string: str) -> str:
            """Transform snake_case to camelCase."""
            return camelize(string, uppercase_first_letter=False)

    def serialize(self):
        """Return serialized representation of Resource."""
        return self.dict(exclude_none=True, by_alias=True)

    @classmethod
    def deserialize(cls: Type[ResourceType], value: dict) -> ResourceType:
        """Deserialize into VerificationMethod."""
        with wrap_validation_error(
            ValueError,
            message="Failed to deserialize {}".format(cls.__name__),
        ):
            return parse_obj_as(cls, value)

    @classmethod
    def deserialize_into(cls, value: dict, type_: Type[ResourceType]) -> ResourceType:
        """Deserialize resource into type_."""
        with wrap_validation_error(
            ValueError,
            message="Failed to deserialize {}".format(cls.__name__),
        ):
            return parse_obj_as(type_, value)

    @classmethod
    def _fill_in_required_literals(cls, **kwargs) -> Dict[str, Any]:
        """Return dictionary of field name to value from literals."""
        for field in cls.__fields__.values():
            if (
                field.required
                and is_literal(field.type_)
                and (field.name not in kwargs or kwargs[field.name] is None)
            ):
                kwargs[field.name] = get_literal_values(field.type_)[0]
        return kwargs

    @classmethod
    def _overwrite_none_with_defaults(cls, **kwargs) -> Dict[str, Any]:
        """Overwrite none values in kwargs with defaults for corresponding field."""
        for field in cls.__fields__.values():
            if field.name in kwargs and kwargs[field.name] is None:
                kwargs[field.name] = field.get_default()
        return kwargs

    @classmethod
    def make(cls: Type[ResourceType], **kwargs) -> ResourceType:
        """Create instance of class, filling in literals."""
        kwargs = cls._fill_in_required_literals(**kwargs)
        kwargs = cls._overwrite_none_with_defaults(**kwargs)
        return cls(**kwargs)
