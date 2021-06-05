"""Generic DID Document Classes.

If using Python 3.7+, these can be used to simplify subclassing a DID Document.
These classes are experimental and subject to change without notice. Use at
your own risk.
"""

import sys

from typing import TypeVar, Optional, List, Union
from .doc import DIDDocumentRoot, BasicDIDDocument
from ..verification_method import VerificationMethod
from ..service import Service
from ..did_url import DIDUrl

if sys.version_info >= (3, 7):  # pragma: no cover
    # In Python 3.7+, we can use Generics with Pydantic to simplify subclassing
    from pydantic.generics import GenericModel
    from typing import Generic

    VM = TypeVar("VM", bound=VerificationMethod)
    SV = TypeVar("SV", bound=Service)
    Methods = Optional[List[VM]]
    Relationships = Optional[List[Union[DIDUrl, VM]]]
    Services = Optional[List[SV]]

    class GenericDIDDocumentRoot(DIDDocumentRoot, GenericModel, Generic[VM, SV]):
        """DID Document Root with Generics."""

        verification_method: Methods[VM] = None
        authentication: Relationships[VM] = None
        assertion_method: Relationships[VM] = None
        key_agreement: Relationships[VM] = None
        capability_invocation: Relationships[VM] = None
        capability_delegation: Relationships[VM] = None
        service: Services[SV] = None

    class GenericBasicDIDDocument(BasicDIDDocument, GenericModel, Generic[VM, SV]):
        """BasicDIDDocument with Generics."""

        verification_method: Methods[VM] = None
        authentication: Relationships[VM] = None
        assertion_method: Relationships[VM] = None
        key_agreement: Relationships[VM] = None
        capability_invocation: Relationships[VM] = None
        capability_delegation: Relationships[VM] = None
        service: Services[SV] = None
