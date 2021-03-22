"""Verification Relationship"""

from typing import List, Union

from voluptuous import All, Schema, Switch

from ..did_url import DIDUrl
from .verification_method import VerificationMethod


class VerificationRelationship:
    """Verification Relationship."""

    validate = Schema(
        [
            Switch(
                All(str, DIDUrl.validate),
                VerificationMethod.validate,
            )
        ]
    )

    def __init__(self, items: List[Union[DIDUrl, VerificationMethod]]):
        """Initialize verification relationship."""
        self.items = items

    def __bool__(self):
        """Return whether this relationship is empty or not."""
        return bool(self.items)

    def __contains__(self, item: VerificationMethod):
        if not isinstance(item, (DIDUrl, VerificationMethod)):
            return False
        return item in self.items or (
            isinstance(item, VerificationMethod) and item.id in self.items
        )

    def serialize(self):
        """Serialize this relationship."""

        def _serialize_item(item):
            if isinstance(item, DIDUrl):
                return str(item)
            if isinstance(item, VerificationMethod):
                return item.serialize()
            raise ValueError(
                "Unexpected type {} in VerificationRelationship".format(type(item))
            )

        return list(map(_serialize_item, self.items))

    @classmethod
    def deserialize(cls, value: List[Union[str, dict]]):
        """Deserialize into relationship."""
        value = cls.validate(value)
        deserializer = Schema(
            [Switch(All(str, DIDUrl.parse), VerificationMethod.deserialize)]
        )
        return cls(deserializer(value))
