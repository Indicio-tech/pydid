"""Integration tests using uni-resolver."""

import json
import logging
from pathlib import Path

import pytest

from pydid.doc.doc import BasicDIDDocument
from pydid.doc.corrections import insert_missing_ids
from pydid.validation import coerce

DOCS_PATH = Path(__file__).parent / "test_docs.json"
DOCS = json.loads(DOCS_PATH.read_text())
LOGGER = logging.getLogger(__name__)


@pytest.mark.int
@pytest.mark.parametrize("doc", DOCS)
def test_uniresolver_docs(caplog, doc):
    caplog.set_level(logging.INFO)
    LOGGER.info("Doc\n%s", json.dumps(doc, indent=2))
    coerce([insert_missing_ids])(BasicDIDDocument).deserialize(
        doc,
    )
