"""DID Document Object."""

from typing import List

from voluptuous import All, Required, Schema, Union, Url

from ..did import DID
from ..did_url import DIDUrl
from .service import Service
from .verification_method import VerificationMethod
from .verification_relationship import VerificationRelationship


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

    def __init__(
        self,
        id_: DID,
        *,
        context: List[str] = None,
        also_known_as: List[str] = None,
        controller: List[str] = None,
        verification_method: List[VerificationMethod] = None,
        authentication: VerificationRelationship = None,
        assertion_method: VerificationRelationship = None,
        key_agreement: VerificationRelationship = None,
        capability_invocation: VerificationRelationship = None,
        capability_delegation: VerificationRelationship = None,
        service: List[Service] = None
    ):
        """Create DIDDocument."""
        self._id = id_
        self._context = context
        self._verifcation_methods: List[VerificationMethod] = []
        self._services: List[Service] = []
        self._index = {}

    def dereference(self, reference: DIDUrl):
        """Dereference a DID URL to a document resource."""
        return self

    def serialize(self):
        """Serialize DID Document."""
        return {}

    @classmethod
    def deserialize(cls, value: dict):
        """Deserialize DID Document."""

        return cls(
            value["id"],
            context=value.get("@context"),
            also_known_as=value.get("alsoKnownAs"),
            controller=value.get("controller"),
            verification_method=value.get("verificationMethod"),
            authentication=value.get("authentication"),
            assertion_method=value.get("assertionMethod"),
            key_agreement=value.get("keyAgreement"),
            capability_invocation=value.get("capabilityInvocation"),
            capability_delegation=value.get("capabilityDelegation"),
            service=value.get("service"),
        )
