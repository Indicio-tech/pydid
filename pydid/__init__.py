"""PyDID"""

import logging
from typing import Callable, List, Optional, Type

from .common import DIDError
from .did import DID, InvalidDIDError
from .did_url import DIDUrl, InvalidDIDUrlError
from .doc.builder import DIDDocumentBuilder
from .doc.doc import (
    BaseDIDDocument,
    BasicDIDDocument,
    DIDDocument,
    NonconformantDocument,
)
from .resource import Resource
from .service import DIDCommService, Service
from .verification_method import (
    VerificationMaterial,
    VerificationMaterialUnknown,
    VerificationMethod,
)
from .doc import generic, corrections

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
    "generic",
    "corrections",
]


LOGGER = logging.getLogger(__name__)


def deserialize_document(
    value: dict,
    corrections: Optional[List[Callable]] = None,
    *,
    strict: bool = False,
    cls: Type[BaseDIDDocument] = None,
) -> BaseDIDDocument:
    """Deserialize a document from a dictionary."""
    if corrections:
        for correction in corrections:
            value = correction(value)

    cls = cls or DIDDocument
    if strict:
        return cls.deserialize(value)
    try:
        return cls.deserialize(value)
    except ValueError as error:
        LOGGER.warning("Failed to deserialize document: %s", error)
        LOGGER.info("Parsing document as non-conformant doc")

    return NonconformantDocument.deserialize(value)
