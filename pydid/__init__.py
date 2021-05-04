"""PyDID"""

from .common import DIDError
from .did import DID, InvalidDIDError
from .did_url import DIDUrl, InvalidDIDUrlError
from .doc.doc import DIDDocument, BasicDIDDocument
from .doc.builder import DIDDocumentBuilder
from .verification_method import (
    VerificationMethod,
    VerificationMaterial,
    VerificationMaterialUnknown,
)
from .service import Service, DIDCommService
from .resource import Resource

__all__ = [
    "BasicDIDDocument",
    "DID",
    "DIDCommService",
    "DIDDocument",
    "DIDDocumentBuilder",
    "DIDDocumentError",
    "DIDError",
    "DIDUrl",
    "InvalidDIDError",
    "InvalidDIDUrlError",
    "Service",
    "VerificationMethod",
    "VerificationMaterial",
    "VerificationMaterialUnknown",
    "Resource",
]
