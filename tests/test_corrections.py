"""Test DID Document corrections."""

import pytest

from pydid.doc.corrections import insert_missing_ids


def test_insert_missing_ids():
    inserted = insert_missing_ids(
        {
            "id": "did:example:123",
            "verificationMethod": [{"the present values": "don't matter here"}],
        }
    )
    assert inserted["verificationMethod"][0]["id"]


def test_insert_missing_ids_x():
    with pytest.raises(ValueError):
        insert_missing_ids({})
