"""DID Doc Verification Method."""

from voluptuous import Schema, All, Invalid, Union
from ..did import DID
from ..did_url import DIDUrl
from . import DIDDocError


class InvalidVerificationMaterial(DIDDocError, Invalid):
    """Error raised when verification material is invalid."""


def verification_material(value):
    """Validate Verification Material key."""
    if "publicKey" not in value:
        raise InvalidVerificationMaterial("Invalid")
    return value


class VerificationMethod:
    """Representation of DID Document Verification Methods."""

    Schema = Schema(
        {
            "id": All(str, DIDUrl.validate),
            "type": str,
            "controller": All(str, DID.validate),
            All(str, verification_material): Union(str, dict),
        },
        required=True,
    )
