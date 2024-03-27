"""DID Document classes."""

from .builder import (
    DIDDocumentBuilder,
    RelationshipBuilder,
    ServiceBuilder,
    VerificationMethodBuilder,
)
from .doc import (
    BasicDIDDocument,
    DIDDocument,
    DIDDocumentError,
    DIDDocumentRoot,
    IdentifiedResourceMismatch,
    IDNotFoundError,
)

__all__ = [
    "DIDDocumentError",
    "IdentifiedResourceMismatch",
    "IDNotFoundError",
    "DIDDocumentRoot",
    "BasicDIDDocument",
    "DIDDocument",
    "VerificationMethodBuilder",
    "RelationshipBuilder",
    "ServiceBuilder",
    "DIDDocumentBuilder",
]
