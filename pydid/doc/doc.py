"""DID Document Object."""

from voluptuous import Schema, All, Union, Url, Required
from ..did import DID
from .verification_method import VerificationMethod
from .verification_relationship import VerificationRelationship
from .service import Service


class DIDDocument:
    """Representation of DID Document."""

    validate = Schema(
        {
            Required("@context"): Union(Url(), [Url()]),
            Required("id"): All(str, DID.validate),
            "alsoKnownAs": [str],
            "controller": Union(All(str, DID.validate), [DID.validate]),
            "verificationMethod": [VerificationMethod.validate],
            "authentication": VerificationRelationship.validate,
            "assertionMethod": VerificationRelationship.validate,
            "keyAgreement": VerificationRelationship.validate,
            "capabilityInvocation": VerificationRelationship.validate,
            "capabilityDelegation": VerificationRelationship.validate,
            "service": [Service.validate],
        }
    )
