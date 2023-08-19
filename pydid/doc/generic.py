"""Generic DID Document Classes.

If using Python 3.7+, these can be used to simplify subclassing a DID Document.
These classes are experimental and subject to change without notice. Use at
your own risk.
"""

import sys
from typing import List, Optional, TypeVar, Union

from pydantic import BaseModel

from ..did_url import DIDUrl
from ..service import Service
from ..verification_method import VerificationMethod
from .doc import BasicDIDDocument, DIDDocumentRoot

if sys.version_info >= (3, 7):  # pragma: no cover
    from typing import Generic

    VM = TypeVar("VM", bound=VerificationMethod)
    SV = TypeVar("SV", bound=Service)
    Methods = Optional[List[VM]]
    Relationships = Optional[List[Union[DIDUrl, VM]]]
    Services = Optional[List[SV]]

    class GenericDIDDocumentRoot(DIDDocumentRoot, BaseModel, Generic[VM, SV]):
        """DID Document Root with Generics."""

        verification_method: Methods[VM] = None
        authentication: Relationships[VM] = None
        assertion_method: Relationships[VM] = None
        key_agreement: Relationships[VM] = None
        capability_invocation: Relationships[VM] = None
        capability_delegation: Relationships[VM] = None
        service: Services[SV] = None

    class GenericBasicDIDDocument(BasicDIDDocument, BaseModel, Generic[VM, SV]):
        """BasicDIDDocument with Generics."""

        verification_method: Methods[VM] = None
        authentication: Relationships[VM] = None
        assertion_method: Relationships[VM] = None
        key_agreement: Relationships[VM] = None
        capability_invocation: Relationships[VM] = None
        capability_delegation: Relationships[VM] = None
        service: Services[SV] = None
