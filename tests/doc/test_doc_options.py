"""Test DID Doc options."""

from pydid.doc.doc_options import DIDDocumentOption
from pydid.doc.verification_method_options import VerificationMethodOptions


def test_vm_allow_type_list():
    assert DIDDocumentOption.apply(
        {
            "verificationMethod": [{"type": ["abc", "123"]}, {"type": ["123", "abc"]}],
            "authentication": ["ref", {"type": ["abc", "123"]}],
            "assertionMethod": [{"type": ["123", "abc"]}],
            "keyAgreement": [{"type": "123"}, "ref"],
        },
        {VerificationMethodOptions.allow_type_list},
    ) == {
        "verificationMethod": [{"type": "abc"}, {"type": "123"}],
        "authentication": ["ref", {"type": "abc"}],
        "assertionMethod": [{"type": "123"}],
        "keyAgreement": [{"type": "123"}, "ref"],
    }
