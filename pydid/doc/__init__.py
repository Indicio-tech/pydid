"""DID Document classes."""

from .doc import (
    IdentifiedResourceMismatch,
    IDNotFoundError,
    DIDDocumentRoot,
    BasicDIDDocument,
    DIDDocument,
)

from .builder import (
    VerificationMethodBuilder,
    RelationshipBuilder,
    ServiceBuilder,
    DIDDocumentBuilder,
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
