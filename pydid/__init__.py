"""PyDID"""

from .common import DIDError
from .did import DID, InvalidDIDError
from .did_url import DIDUrl, InvalidDIDUrlError
from .doc import DIDDocumentError
from .doc.doc import DIDDocument, DIDDocumentValidationError
from .doc.builder import DIDDocumentBuilder
from .doc.verification_method import (
    VerificationMethod,
    VerificationSuite,
    VerificationMethodValidationError,
)
from .doc.service import Service, ServiceValidationError
from .doc.didcomm_service import DIDCommService

__all__ = [
    "DID",
    "DIDCommService",
    "DIDDocument",
    "DIDDocumentBuilder",
    "DIDDocumentError",
    "DIDDocumentValidationError",
    "DIDError",
    "DIDUrl",
    "InvalidDIDError",
    "InvalidDIDUrlError",
    "Service",
    "ServiceValidationError",
    "VerificationMethod",
    "VerificationMethodValidationError",
    "VerificationSuite",
]
