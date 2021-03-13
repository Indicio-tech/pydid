"""Verification Relationship"""

from voluptuous import Schema, Union
from .verification_method import VerificationMethod
from ..did_url import DIDUrl


class VerificationRelationship:
    """Verification Relationship."""
    Schema = Schema([
        Union(
            DIDUrl.validate, VerificationMethod.Schema,
            discriminant=lambda val, alt: [alt[0]] if isinstance(val, str) else [alt[1]]
        )
    ])
