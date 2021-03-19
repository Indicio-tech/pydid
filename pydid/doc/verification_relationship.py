"""Verification Relationship"""

import typing
from typing import List

from voluptuous import All, Schema, Union

from ..did_url import DIDUrl
from .verification_method import VerificationMethod


class VerificationRelationship:
    """Verification Relationship."""

    validate = Schema(
        [
            Union(
                All(str, DIDUrl.validate),
                VerificationMethod.validate,
            )
        ]
    )

    def __init__(self, items: List[typing.Union[DIDUrl, VerificationMethod]]):
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
    def deserialize(cls, value: List[typing.Union[str, dict]]):
        """Deserialize into relationship."""

        def _deserialize_item(item):
            if isinstance(item, str):
                return DIDUrl.parse(item)
            if isinstance(item, dict):
                return VerificationMethod.deserialize(item)
            raise ValueError(
                "Unexpected type {} in VerificationRelationship".format(type(item))
            )

        return cls(list(map(_deserialize_item, value)))
