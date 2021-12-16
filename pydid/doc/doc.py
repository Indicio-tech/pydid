"""DID Document Object."""

from abc import ABC
from typing import Any, List, Optional, Union

from pydantic import Field, root_validator, validator
from typing_extensions import Annotated

from ..did import DID, InvalidDIDError
from ..did_url import DIDUrl, InvalidDIDUrlError
from ..resource import IndexedResource, Resource
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

    context: Annotated[
        List[Union[str, dict]], Field(alias="@context")
    ] = [  # noqa: F722
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
        if "publicKey" in values:
            values["verificationMethod"] = values["publicKey"]
        return values


class BaseDIDDocument(DIDDocumentRoot, IndexedResource, ABC):
    """Abstract BaseDIDDocument class."""

    @property
    def is_nonconformant(self):
        """Return whether doc is non-conformant."""
        return isinstance(self, NonconformantDocument)

    @property
    def is_conformant(self):
        """Return whether doc is conformant."""
        return not isinstance(self, NonconformantDocument)


class BasicDIDDocument(BaseDIDDocument):
    """Basic DID Document."""

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

    def dereference(self, reference: Union[str, DIDUrl]) -> Resource:
        """Dereference a DID URL to a document resource."""
        if isinstance(reference, str):
            reference = DIDUrl.parse(reference)
        if not reference.did:
            reference = reference.as_absolute(self.id)

        if reference not in self._index:
            raise IDNotFoundError("ID {} not found in document".format(reference))
        return self._index[reference]


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


class NonconformantDocument(BaseDIDDocument):
    """Container for non-conformant documents.

    This container allows us to interact with these documents without going
    through the more rigorous validation.
    """

    id: DID
    context: Annotated[Any, Field(alias="@context")] = None  # noqa: F722
    also_known_as: Any = None
    controller: Any = None
    verification_method: Any = None
    authentication: Any = None
    assertion_method: Any = None
    key_agreement: Any = None
    capability_invocation: Any = None
    capability_delegation: Any = None
    service: Any = None

    def _index_resources(self):
        """Index resources by ID.

        This is done in the most permissive way possible. ID collisions will
        result in overwritten data instead of raising an error.
        """

        def _indexer(item):
            if isinstance(item, list):
                # Recurse on lists
                for subitem in item:
                    _indexer(subitem)
                return

            if not isinstance(item, dict):
                # Only dictionaries are indexable
                return

            if "id" not in item:
                # Only dictionaries with IDs are indexed
                return

            # Attempt to account for relative IDs
            try:
                ref = DIDUrl(item["id"])
                if not ref.did:
                    key = ref.as_absolute(self.id)
                else:
                    key = ref
            except (InvalidDIDError, InvalidDIDUrlError):
                key = item["id"]

            self._index[key] = Resource(**item)

            # Recurse
            for value in item.values():
                _indexer(value)

        for _, value in self:
            _indexer(value)

    def dereference(self, reference: Union[str, DIDUrl]) -> Resource:
        """Dereference a DID URL to a document resource."""
        if isinstance(reference, str):
            reference = DIDUrl.parse(reference)
        if not reference.did:
            reference = reference.as_absolute(self.id)

        if reference not in self._index:
            raise IDNotFoundError("ID {} not found in document".format(reference))
        return self._index[reference]
