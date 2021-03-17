"""Test VerificationRelationship."""

import pytest
from voluptuous import MultipleInvalid

from pydid.doc.verification_relationship import VerificationRelationship

from .test_verification_method import INVALID_VMETHOD0, VMETHOD0

RELATIONSHIP0 = ["did:example:123#keys-1", VMETHOD0]


def test_simple():
    VerificationRelationship.validate(RELATIONSHIP0)


def test_invalid_method():
    with pytest.raises(MultipleInvalid):
        VerificationRelationship.validate(["did:example:123#keys-1", INVALID_VMETHOD0])


def test_invalid_reference():
    with pytest.raises(MultipleInvalid):
        VerificationRelationship.validate(["1234", VMETHOD0])


def test_serialization():
    rel = VerificationRelationship.deserialize(RELATIONSHIP0)
    assert rel.serialize() == RELATIONSHIP0
