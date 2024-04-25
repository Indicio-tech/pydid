"""Resource class that forms the base of all DID Document components."""

import json
from abc import ABC, abstractmethod
from typing import Any, Dict, Type, TypeVar

import typing_extensions
from pydantic import BaseModel, ConfigDict, TypeAdapter, alias_generators
from typing_extensions import Literal

from .validation import wrap_validation_error

ResourceType = TypeVar("ResourceType", bound="Resource")


if hasattr(typing_extensions, "get_args"):  # pragma: no cover
    from typing_extensions import get_args, get_origin

    def get_literal_values(literal):
        """Return the args of a literal."""
        return get_args(literal)

    def is_literal(type_):
        """Return if type is literal."""
        return get_origin(type_) is Literal

else:  # pragma: no cover
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

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
        alias_generator=alias_generators.to_camel,
    )

    def serialize(self):
        """Return serialized representation of Resource."""
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def deserialize(cls: Type[ResourceType], value: dict) -> ResourceType:
        """Deserialize into Resource subtype."""
        with wrap_validation_error(
            ValueError,
            message=f"Failed to deserialize {cls.__name__}",
        ):
            resource_adapter = TypeAdapter(cls)
            return resource_adapter.validate_python(value)

    @classmethod
    def from_json(cls, value: str):
        """Deserialize Resource from JSON."""
        loaded: dict = json.loads(value)
        return cls.deserialize(loaded)

    def to_json(self):
        """Serialize Resource to JSON."""
        return self.model_dump_json(exclude_none=True, by_alias=True)

    @classmethod
    def _fill_in_required_literals(cls, **kwargs) -> Dict[str, Any]:
        """Return dictionary of field name to value from literals."""
        for field in cls.model_fields.values():
            field_name = field.alias
            field_type = field.annotation
            if (
                field.is_required()
                and is_literal(field_type)
                and (field_name not in kwargs or kwargs[field_name] is None)
            ):
                kwargs[field_name] = get_literal_values(field_type)[0]
        return kwargs

    @classmethod
    def _overwrite_none_with_defaults(cls, **kwargs) -> Dict[str, Any]:
        """Overwrite none values in kwargs with defaults for corresponding field."""
        for field in cls.model_fields.values():
            field_name = field.alias
            if field_name in kwargs and kwargs[field_name] is None:
                kwargs[field_name] = field.get_default()
        return kwargs

    @classmethod
    def make(cls: Type[ResourceType], **kwargs) -> ResourceType:
        """Create instance of class, filling in literals."""
        kwargs = cls._fill_in_required_literals(**kwargs)
        kwargs = cls._overwrite_none_with_defaults(**kwargs)
        return cls(**kwargs)


class IndexedResource(Resource, ABC):
    """Resource with index for supporting dereferencing nested objects."""

    _index: dict = {}

    def __init__(self, **data):
        """Initialize Resource."""
        super().__init__(**data)
        self._index_resources()

    @abstractmethod
    def _index_resources(self):
        """Index nested resources."""

    @abstractmethod
    def dereference(self, reference: str) -> Resource:
        """Dereference a nested object."""

    def dereference_as(self, typ: Type[ResourceType], reference: str) -> ResourceType:
        """Dereference a resource to a specific type."""
        with wrap_validation_error(
            ValueError,
            message=f"Dereferenced resource {reference} could not be parsed as {typ}",
        ):
            resource = self.dereference(reference)
            resource_adapter: TypeAdapter[ResourceType] = TypeAdapter(typ)
            return resource_adapter.validate_python(resource.model_dump())

    @classmethod
    def model_construct(cls, **data):
        """Construct and index."""
        resource = super(Resource, cls).model_construct(**data)
        resource._index_resources()
        return resource
