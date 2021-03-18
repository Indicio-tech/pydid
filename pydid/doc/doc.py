"""DID Document Object."""

from typing import List

from voluptuous import ALLOW_EXTRA, All, Coerce, Required, Schema, Union, Url

from ..did import DID
from ..did_url import DIDUrl
from ..validation import As
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
        },
        extra=ALLOW_EXTRA,
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
        service: List[Service] = None,
        **extra
    ):
        """Create DIDDocument."""
        self.id = id_
        self.context = context
        self.also_known_as = also_known_as
        self.controller = controller
        self.verification_method = verification_method
        self.authentication = authentication
        self.assertion_method = assertion_method
        self.key_agreement = key_agreement
        self.capability_invocation = capability_invocation
        self.capability_delegation = capability_delegation
        self.service = service

    def dereference(self, reference: DIDUrl):
        """Dereference a DID URL to a document resource."""
        return self

    def serialize(self):
        """Serialize DID Document."""

        def _unwrap_if_list_of_one(value):
            if value and len(value) == 1:
                return value[0]
            return value

        def _serialize(item):
            return item.serialize()

        mapping = Schema(
            {
                As("context", "@context"): _unwrap_if_list_of_one,
                "id": Coerce(str),
                As("also_known_as", "alsoKnownAs"): [str],
                "controller": All([Coerce(str)], _unwrap_if_list_of_one),
                As("verification_method", "verificationMethod"): [_serialize],
                "authentication": _serialize,
                As("assertion_method", "assertionMethod"): _serialize,
                As("key_agreement", "KeyAgreement"): _serialize,
                As("capability_invocation", "capabilityInvocation"): _serialize,
                As("capability_delegation", "capabilityDelegation"): _serialize,
                "service": _serialize,
            }
        )
        return mapping(
            {key: value for key, value in self.__dict__.items() if value is not None}
        )

    @classmethod
    def deserialize(cls, value: dict):
        """Deserialize DID Document."""
        value = cls.validate(value)

        def _single_to_list(value):
            if isinstance(value, list):
                return value
            return [value]

        mapping = Schema(
            {
                As("id", "id_"): Coerce(DID),
                As("@context", "context"): _single_to_list,
                As("alsoKnownAs", "also_known_as"): [str],
                "controller": All(_single_to_list, [Coerce(DID)]),
                As("verificationMethod", "verification_method"): [
                    VerificationMethod.deserialize
                ],
                "authentication": VerificationRelationship.deserialize,
                As(
                    "assertionMethod", "assertion_method"
                ): VerificationRelationship.deserialize,
                As(
                    "keyAgreement", "key_agreement"
                ): VerificationRelationship.deserialize,
                As(
                    "capabilityInvocation", "capability_invocation"
                ): VerificationRelationship.deserialize,
                As(
                    "capabilityDelegation", "capability_delegation"
                ): VerificationRelationship.deserialize,
                "service": [Service.deserialize],
            },
        )

        value = mapping(value)
        return cls(**value)
