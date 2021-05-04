"""Resource class that forms the base of all DID Document components."""

from typing import Type, TypeVar

from pydantic import BaseModel, Extra, parse_obj_as
from inflection import camelize

from ..validation import wrap_validation_error


ResourceType = TypeVar("ResourceType", bound="Resource")


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
