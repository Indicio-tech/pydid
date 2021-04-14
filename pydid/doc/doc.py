"""DID Document Object."""

import json
from typing import List, Union, Optional, Type

from pydantic import AnyUrl, Field, validator, create_model
from typing_extensions import Annotated

from ..did import DID
from ..did_url import DIDUrl
from . import DIDDocumentError
from .service import Service, DIDCommService
from .verification_method import (
    VerificationMethod,
    KnownVerificationMethods,
    UnknownVerificationMethod,
)
from .resource import Resource
from ..validation import single_to_list


class IdentifiedResourceMismatch(DIDDocumentError):
    """Raised when two or more of the same ID point to differing resources."""


class IDNotFoundError(DIDDocumentError):
    """Raised when Resource ID not found in DID Document."""


class DIDDocument(Resource):
    """Representation of DID Document."""

    # pylint: disable=unsubscriptable-object

    context: Annotated[List[AnyUrl], Field(alias="@context")] = [  # noqa: F722
        "https://www.w3.org/ns/did/v1"
    ]
    id: DID
    also_known_as: Optional[List[str]] = None
    controller: Optional[List[str]] = None
    verification_method: Optional[List[VerificationMethod]] = None
    authentication: Optional[List[Union[DIDUrl, VerificationMethod]]] = None
    assertion_method: Optional[List[Union[DIDUrl, VerificationMethod]]] = None
    key_agreement: Optional[List[Union[DIDUrl, VerificationMethod]]] = None
    capability_invocation: Optional[List[Union[DIDUrl, VerificationMethod]]] = None
    capability_delegation: Optional[List[Union[DIDUrl, VerificationMethod]]] = None
    service: Optional[List[Service]] = None
    _index: dict = {}

    def __init__(self, **data):
        """Create DIDDocument."""
        super().__init__(**data)
        self._index_resources()

    @validator("context", "controller", pre=True)
    @classmethod
    def listify(cls, value):
        """Transform values into lists that are allowed to be a list or single."""
        print(value)
        return single_to_list(value)

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
    def did(self):
        """Return the DID representation of id."""
        return DID(self._id)

    def dereference(self, reference: Union[str, DIDUrl]):
        """Dereference a DID URL to a document resource."""
        if isinstance(reference, str):
            reference = DIDUrl.parse(reference)

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
    def using(
        cls,
        name: str,
        verification_method: Type[VerificationMethod] = None,
        service: Type[Service] = None,
    ):
        """Define a new model using given types for verification methods and services."""
        return create_model(
            name,
            __base__=cls,
            verification_method=(
                Optional[List[verification_method or VerificationMethod]],
                None,
            ),
            authentication=(
                Optional[
                    List[Union[DIDUrl, verification_method or VerificationMethod]]
                ],
                None,
            ),
            assertion_method=(
                Optional[
                    List[Union[DIDUrl, verification_method or VerificationMethod]]
                ],
                None,
            ),
            key_agreement=(
                Optional[
                    List[Union[DIDUrl, verification_method or VerificationMethod]]
                ],
                None,
            ),
            capability_invocation=(
                Optional[
                    List[Union[DIDUrl, verification_method or VerificationMethod]]
                ],
                None,
            ),
            capability_delegation=(
                Optional[
                    List[Union[DIDUrl, verification_method or VerificationMethod]]
                ],
                None,
            ),
            service=(Optional[List[service or Service]], None),
        )


DIDDocumentV1 = DIDDocument.using(
    "DIDDocumentV1",
    verification_method=Union[KnownVerificationMethods, UnknownVerificationMethod],
    service=Union[DIDCommService, Service],
)
