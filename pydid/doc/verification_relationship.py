"""Verification Relationship"""

from voluptuous import Schema, Union, All
from .verification_method import VerificationMethod
from ..did_url import DIDUrl


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
