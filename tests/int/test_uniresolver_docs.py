"""Integration tests using uni-resolver."""

import json
import logging
from pathlib import Path

import pytest

from pydid import DIDDocument
from pydid.options import (
    doc_allow_public_key,
    doc_insert_missing_ids,
    vm_allow_controller_list,
    vm_allow_missing_controller,
    vm_allow_type_list,
)

DOCS_PATH = Path(__file__).parent / "test_docs.json"
DOCS = json.loads(DOCS_PATH.read_text())

LOGGER = logging.getLogger(__name__)


@pytest.mark.int
@pytest.mark.parametrize("doc", DOCS)
def test_uniresolver_docs(caplog, doc):
    caplog.set_level(logging.INFO)
    LOGGER.info("Doc:\n%s", json.dumps(doc, indent=2))
    assert DIDDocument.deserialize(
        doc,
        options={
            doc_allow_public_key,
            doc_insert_missing_ids,
            vm_allow_controller_list,
            vm_allow_missing_controller,
            vm_allow_type_list,
        },
    )
