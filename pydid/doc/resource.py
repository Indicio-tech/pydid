"""Resource class that forms the base of all DID Document components."""

from typing import Type, Set

from pydantic import BaseModel, Extra, parse_obj_as

from ..did import DID
from ..did_url import DIDUrl
from ..validation import wrap_validation_error, Option


class Resource(BaseModel):
    """Base class for DID Document components."""

    class Config:
        """Configuration for Resources."""

        extra = Extra.allow
        json_encoders = {DID: str, DIDUrl: str}

        @classmethod
        def alias_generator(cls, string: str) -> str:
            """Transform snake_case to camelCase."""
            split = string.split("_")
            return "".join([split[0]] + [word.capitalize() for word in split[1:]])

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
    def deserialize(
        cls, value: dict, *, type_: Type["Resource"] = None, options: Set[Option] = None
    ) -> "Resource":
        """Deserialize into VerificationMethod."""
        with wrap_validation_error(
            ValueError,
            message="Failed to deserialize {}".format(cls.__name__),
        ):
            # Apply options
            if options:
                for option in sorted(options, key=lambda opt: opt.priority):
                    value = option.apply(value)

            if type_:
                return parse_obj_as(type_, value)

            return parse_obj_as(cls, value)
