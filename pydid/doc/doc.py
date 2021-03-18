"""DID Document Object."""

import typing
from typing import List

from voluptuous import ALLOW_EXTRA, All, Coerce, Required, Schema, Union, Url
from voluptuous import validate as validate_args

from ..did import DID
from ..did_url import DIDUrl
from ..validation import Into
from .service import Service
from .verification_method import VerificationMethod
from .verification_relationship import VerificationRelationship
from . import DIDDocError
from ..validation import unwrap_if_list_of_one, single_to_list, serialize


class DuplicateResourceID(DIDDocError):
    """Raised when IDs in Document are not unique."""


class ResourceIDNotFound(DIDDocError):
    """Raised when Resource ID not found in DID Document."""


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
        self.extra = extra

        self._index = {}
        self._index_resources()

    def _index_resources(self):
        """Index resources by ID.

        IDs must be globally unique. Collisions are cause for error.
        """

        def _indexer(item):
            if not item:
                # Attribute isn't set
                return
            if isinstance(item, DIDUrl):
                # We don't index references
                return
            if isinstance(item, list):
                for subitem in item:
                    _indexer(subitem)
                    return
            if isinstance(item, VerificationRelationship):
                for subitem in item.items:
                    _indexer(subitem)
                    return

            assert isinstance(item, (VerificationMethod, Service))
            if item.id in self._index:
                raise DuplicateResourceID(
                    "ID {} already found in Index".format(item.id)
                )

            self._index[item.id] = item

        for item in (
            self.verification_method,
            self.authentication,
            self.assertion_method,
            self.key_agreement,
            self.capability_invocation,
            self.capability_delegation,
        ):
            _indexer(item)

    @validate_args(reference=Union(DIDUrl, All(str, DIDUrl.parse)))
    def dereference(self, reference: typing.Union[str, DIDUrl]):
        """Dereference a DID URL to a document resource."""
        if reference not in self._index:
            raise ResourceIDNotFound("ID {} not found in document".format(reference))
        return self._index[reference]

    def serialize(self):
        """Serialize DID Document."""
        mapping = Schema(
            {
                Into("context", "@context"): unwrap_if_list_of_one,
                "id": Coerce(str),
                Into("also_known_as", "alsoKnownAs"): [str],
                "controller": All([Coerce(str)], unwrap_if_list_of_one),
                Into("verification_method", "verificationMethod"): [serialize],
                "authentication": serialize,
                Into("assertion_method", "assertionMethod"): serialize,
                Into("key_agreement", "KeyAgreement"): serialize,
                Into("capability_invocation", "capabilityInvocation"): serialize,
                Into("capability_delegation", "capabilityDelegation"): serialize,
                "service": serialize,
            },
            extra=ALLOW_EXTRA,
        )
        value = mapping(
            {
                key: value
                for key, value in self.__dict__.items()
                if value is not None and not key.startswith("_") and not key == "extra"
            }
        )
        return {**value, **self.extra}

    @classmethod
    def deserialize(cls, value: dict):
        """Deserialize DID Document."""
        value = cls.validate(value)
        mapping = Schema(
            {
                Into("id", "id_"): Coerce(DID),
                Into("@context", "context"): single_to_list,
                Into("alsoKnownAs", "also_known_as"): [str],
                "controller": All(single_to_list, [Coerce(DID)]),
                Into("verificationMethod", "verification_method"): [
                    VerificationMethod.deserialize
                ],
                "authentication": VerificationRelationship.deserialize,
                Into(
                    "assertionMethod", "assertion_method"
                ): VerificationRelationship.deserialize,
                Into(
                    "keyAgreement", "key_agreement"
                ): VerificationRelationship.deserialize,
                Into(
                    "capabilityInvocation", "capability_invocation"
                ): VerificationRelationship.deserialize,
                Into(
                    "capabilityDelegation", "capability_delegation"
                ): VerificationRelationship.deserialize,
                "service": [Service.deserialize],
            },
            extra=ALLOW_EXTRA,
        )

        value = mapping(value)
        return cls(**value)
