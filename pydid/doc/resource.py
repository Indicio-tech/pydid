"""Resource class that forms the base of all DID Document components."""

from typing import Type, TypeVar

from pydantic import BaseModel, Extra, parse_obj_as
from inflection import camelize

from ..did import DID
from ..did_url import DIDUrl
from ..validation import wrap_validation_error


T = TypeVar("T", bound="Resource")


class Resource(BaseModel):
    """Base class for DID Document components."""

    class Config:
        """Configuration for Resources."""

        underscore_attrs_are_private = True
        extra = Extra.allow
        json_encoders = {DID: str, DIDUrl: str}

        @classmethod
        def alias_generator(cls, string: str) -> str:
            """Transform snake_case to camelCase."""
            return camelize(string, uppercase_first_letter=False)

    def serialize(self):
        """Return serialized representation of Resource."""
        result = {}
        for key, value in self.dict(by_alias=True).items():
            if key in self.__fields__:
                type_ = self.__fields__[key].type_
                if type_ in Resource.Config.json_encoders:
                    value = Resource.Config.json_encoders[type_](value)

            if isinstance(value, Resource):
                result[key] = value.serialize()
            elif isinstance(value, BaseModel):
                result[key] = value.dict(by_alias=True)
            else:
                result[key] = value

        return result

    @classmethod
    def deserialize(cls: Type[T], value: dict, *, type_: Type[T] = None) -> T:
        """Deserialize into VerificationMethod."""
        with wrap_validation_error(
            ValueError,
            message="Failed to deserialize {}".format(cls.__name__),
        ):
            if type_:
                return parse_obj_as(type_, value)

            return parse_obj_as(cls, value)
