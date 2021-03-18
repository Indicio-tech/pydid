"""DID Document Object."""

import typing
from typing import List

from voluptuous import ALLOW_EXTRA, All, Coerce, Union, Url
from voluptuous import validate as validate_args

from ..did import DID
from ..did_url import DIDUrl
from .service import Service
from .verification_method import VerificationMethod
from .verification_relationship import VerificationRelationship
from . import DIDDocError
from ..validation import unwrap_if_list_of_one, single_to_list, serialize, Properties


class DuplicateResourceID(DIDDocError):
    """Raised when IDs in Document are not unique."""


class ResourceIDNotFound(DIDDocError):
    """Raised when Resource ID not found in DID Document."""


class DIDDocument:
    """Representation of DID Document."""

    properties = Properties(extra=ALLOW_EXTRA)

    def __init__(
        self,
        id: DID,
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
        self._id = id
        self._context = context
        self._also_known_as = also_known_as
        self._controller = controller
        self._verification_method = verification_method
        self._authentication = authentication
        self._assertion_method = assertion_method
        self._key_agreement = key_agreement
        self._capability_invocation = capability_invocation
        self._capability_delegation = capability_delegation
        self._service = service
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
            self.service,
        ):
            _indexer(item)

    @property
    @properties.add(
        data_key="@context",
        required=True,
        validate=Union(Url(), [Url()]),
        serialize=unwrap_if_list_of_one,
        deserialize=single_to_list,
    )
    def context(self):
        """Return context."""
        return self._context

    @property
    @properties.add(
        required=True,
        validate=All(str, DID.validate),
        serialize=Coerce(str),
        deserialize=Coerce(DID),
    )
    def id(self):
        """Return id."""
        return self._id

    @property
    @properties.add(data_key="alsoKnownAs", validate=[str])
    def also_known_as(self):
        """Return also_known_as."""
        return self._also_known_as

    @property
    @properties.add(
        validate=Union(All(str, DID.validate), [DID.validate]),
        serialize=All([Coerce(str)], unwrap_if_list_of_one),
        deserialize=All(single_to_list, [Coerce(DID)]),
    )
    def controller(self):
        """Return controller."""
        return self._controller

    @property
    @properties.add(
        data_key="verificationMethod",
        validate=[VerificationMethod.validate],
        serialize=[serialize],
        deserialize=[VerificationMethod.deserialize],
    )
    def verification_method(self):
        """Return verification_method."""
        return self._verification_method

    @property
    @properties.add(
        validate=VerificationRelationship.validate,
        serialize=serialize,
        deserialize=VerificationRelationship.deserialize,
    )
    def authentication(self):
        """Return authentication."""
        return self._authentication

    @property
    @properties.add(
        data_key="assertionMethod",
        validate=VerificationRelationship.validate,
        serialize=serialize,
        deserialize=VerificationRelationship.deserialize,
    )
    def assertion_method(self):
        """Return assertion_method."""
        return self._assertion_method

    @property
    @properties.add(
        data_key="keyAgreement",
        validate=VerificationRelationship.validate,
        serialize=serialize,
        deserialize=VerificationRelationship.deserialize,
    )
    def key_agreement(self):
        """Return key_agreement."""
        return self._key_agreement

    @property
    @properties.add(
        data_key="capabilityInvocation",
        validate=VerificationRelationship.validate,
        serialize=serialize,
        deserialize=VerificationRelationship.deserialize,
    )
    def capability_invocation(self):
        """Return capability_invocation."""
        return self._capability_invocation

    @property
    @properties.add(
        data_key="capabilityDelegation",
        validate=VerificationRelationship.validate,
        serialize=serialize,
        deserialize=VerificationRelationship.deserialize,
    )
    def capability_delegation(self):
        """Return capability_delegation."""
        return self._capability_delegation

    @property
    @properties.add(
        validate=[Service.validate],
        serialize=[serialize],
        deserialize=[Service.deserialize],
    )
    def service(self):
        """Return service."""
        return self._service

    @validate_args(reference=Union(DIDUrl, All(str, DIDUrl.parse)))
    def dereference(self, reference: typing.Union[str, DIDUrl]):
        """Dereference a DID URL to a document resource."""
        if reference not in self._index:
            raise ResourceIDNotFound("ID {} not found in document".format(reference))
        return self._index[reference]

    @classmethod
    def validate(cls, value):
        """Validate against expected schema."""
        return cls.properties.validate(value)

    def serialize(self):
        """Serialize DID Document."""
        value = self.properties.serialize(self)
        return {**value, **self.extra}

    @classmethod
    def deserialize(cls, value: dict):
        """Deserialize DID Document."""
        value = cls.validate(value)
        value = cls.properties.deserialize(value)
        return cls(**value)
