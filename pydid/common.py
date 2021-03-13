"""Common components."""
import re

DID_PATTERN = re.compile("did:([a-z0-9]+):((?:[a-zA-Z0-9._-]*:)*[a-zA-Z0-9._-]+)")


class DIDError(Exception):
    """General did error."""
