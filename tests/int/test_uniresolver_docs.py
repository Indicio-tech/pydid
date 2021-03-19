"""Integration tests using uni-resolver."""

import json
from pathlib import Path
import pytest
import requests
from pydid import DIDDocument

CONFIG_PATH = Path(__file__).parent / "uniresolver_config.json"
TEST_CONFIG = json.loads(CONFIG_PATH.read_text())
TEST_DIDS = [
    did for driver in TEST_CONFIG["drivers"] for did in driver["testIdentifiers"]
]


@pytest.mark.int
@pytest.mark.parametrize("did", TEST_DIDS)
def test_uniresolver_docs(did):
    resp = requests.get(f"https://dev.uniresolver.io/1.0/identifiers/{did}")
    if resp.ok:
        doc_raw = resp.json()["didDocument"]
        doc = DIDDocument.deserialize(doc_raw)
        assert doc
    else:
        pytest.xfail(f"Failed to retrieve doc: f{resp.content}")
