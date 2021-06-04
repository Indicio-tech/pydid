"""Common components."""
import re

DID_REGEX = "did:([a-z0-9]+):((?:[a-zA-Z0-9._%-]*:)*[a-zA-Z0-9._%-]+)"
DID_PATTERN = re.compile(f"^{DID_REGEX}$")
DID_URL_DID_PART_PATTERN = re.compile(f"^({DID_REGEX})[?/#]")
DID_URL_RELATIVE_FRONT = re.compile("^[?/#].*")


class DIDError(Exception):
    """General did error."""
