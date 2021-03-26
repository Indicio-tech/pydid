"""Export options for use externally."""

from .doc.doc_options import DIDDocumentOption
from .doc.verification_method_options import VerificationMethodOptions
from .doc.didcomm_service_options import ServicesMethodsOptions

doc_allow_public_key = DIDDocumentOption.allow_public_key
doc_insert_missing_ids = DIDDocumentOption.insert_missing_ids
vm_allow_type_list = VerificationMethodOptions.allow_type_list
vm_allow_missing_controller = VerificationMethodOptions.allow_missing_controller
vm_allow_controller_list = VerificationMethodOptions.allow_controller_list
services_allow_empty_endpoints = ServicesMethodsOptions.allow_empty_endpoints

__all__ = [
    "doc_allow_public_key",
    "doc_insert_missing_ids",
    "vm_allow_controller_list",
    "vm_allow_missing_controller",
    "vm_allow_type_list",
    "services_allow_empty_endpoints",
]
