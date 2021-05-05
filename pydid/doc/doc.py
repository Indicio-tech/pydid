"""DID Document Object."""

import json
from typing import List, Optional, Union

from pydantic import Field, root_validator, validator
from typing_extensions import Annotated

from ..did import DID
from ..did_url import DIDUrl
from ..resource import Resource
from ..service import DIDCommService, Service, UnknownService
from ..verification_method import (
    KnownVerificationMethods,
    UnknownVerificationMethod,
    VerificationMethod,
)


class DIDDocumentError(Exception):
    """Base Exception for problems with DID Documents."""


class IdentifiedResourceMismatch(DIDDocumentError):
    """Raised when two or more of the same ID point to differing resources."""


class IDNotFoundError(DIDDocumentError):
    """Raised when Resource ID not found in DID Document."""


class DIDDocumentRoot(Resource):
    """Representation of DID Document."""

    # pylint: disable=unsubscriptable-object

    context: Annotated[List[str], Field(alias="@context")] = [  # noqa: F722
        "https://www.w3.org/ns/did/v1"
    ]
    id: DID
    also_known_as: Optional[List[str]] = None
    controller: Optional[List[DID]] = None
    verification_method: Optional[List[VerificationMethod]] = None
    authentication: Optional[List[Union[DIDUrl, VerificationMethod]]] = None
    assertion_method: Optional[List[Union[DIDUrl, VerificationMethod]]] = None
    key_agreement: Optional[List[Union[DIDUrl, VerificationMethod]]] = None
    capability_invocation: Optional[List[Union[DIDUrl, VerificationMethod]]] = None
    capability_delegation: Optional[List[Union[DIDUrl, VerificationMethod]]] = None
    service: Optional[List[Service]] = None

    @validator("context", "controller", pre=True, allow_reuse=True)
    @classmethod
    def _listify(cls, value):
        """Transform values into lists that are allowed to be a list or single."""
        if value is None:
            return value
        if isinstance(value, list):
            return value
        return [value]

    @root_validator(pre=True, allow_reuse=True)
    @classmethod
    def _allow_publickey_instead_of_verification_method(cls, values: dict):
        """Accept publickKey, transforming to verificationMethod.

        This validator handles a common DID Document mutation.
        """
        if "publickKey" in values:
            values["verificationMethod"] = values["publickKey"]
        return values


class BasicDIDDocument(DIDDocumentRoot):
    """Basic DID Document."""

    _index: dict = {}

    def __init__(self, **data):
        """Create DIDDocument."""
        super().__init__(**data)
        self._index_resources()

    def _index_resources(self):
        """Index resources by ID.

        IDs are not guaranteed to be unique within the document.
        The first instance is stored in the index and subsequent id collisions
        are checked against the original. If they do not match, an error will
        be thrown.
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

            assert isinstance(item, (VerificationMethod, Service))
            if item.id in self._index and item != self._index[item.id]:
                raise IdentifiedResourceMismatch(
                    "ID {} already found in Index and Items do not match".format(
                        item.id
                    )
                )

            if not item.id.did:
                key = item.id.as_absolute(self.id)
            else:
                key = item.id

            self._index[key] = item

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

    def dereference(self, reference: Union[str, DIDUrl]):
        """Dereference a DID URL to a document resource."""
        if isinstance(reference, str):
            reference = DIDUrl.parse(reference)
        if not reference.did:
            reference = reference.as_absolute(self.id)

        if reference not in self._index:
            raise IDNotFoundError("ID {} not found in document".format(reference))
        return self._index[reference]

    @classmethod
    def from_json(cls, value: str):
        """Deserialize DID Document from JSON."""
        doc_raw: dict = json.loads(value)
        return cls.deserialize(doc_raw)

    def to_json(self):
        """Serialize DID Document to JSON."""
        return self.json()

    @classmethod
    def construct(cls, **data):
        """Construct and index."""
        doc = super(Resource, cls).construct(**data)
        doc._index_resources()
        return doc


PossibleMethodTypes = Union[KnownVerificationMethods, UnknownVerificationMethod]
PossibleServiceTypes = Union[DIDCommService, UnknownService]


class DIDDocument(BasicDIDDocument):
    """
    DID Document for DID Spec version 1.0.

    Registered verification method and service types are parsed into specific objects.
    """

    verification_method: Optional[List[PossibleMethodTypes]] = None
    authentication: Optional[List[Union[DIDUrl, PossibleMethodTypes]]] = None
    assertion_method: Optional[List[Union[DIDUrl, PossibleMethodTypes]]] = None
    key_agreement: Optional[List[Union[DIDUrl, PossibleMethodTypes]]] = None
    capability_invocation: Optional[List[Union[DIDUrl, PossibleMethodTypes]]] = None
    capability_delegation: Optional[List[Union[DIDUrl, PossibleMethodTypes]]] = None
    service: Optional[List[PossibleServiceTypes]] = None

    @classmethod
    def deserialize(cls, value: dict) -> "DIDDocument":
        """Wrap deserialization with a basic validation pass before matching to type."""
        DIDDocumentRoot.deserialize(value)
        return super(DIDDocument, cls).deserialize(value)
