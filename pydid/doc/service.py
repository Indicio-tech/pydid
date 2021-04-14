"""DID Doc Service."""

from typing import Union, List

from pydantic import AnyUrl
from typing_extensions import Literal

from ..did_url import DIDUrl
from .resource import Resource


class Service(Resource):
    """Representation of DID Document Services."""

    id: DIDUrl
    type: str
    service_endpoint: Union[DIDUrl, AnyUrl, Literal[""]]


class DIDCommService(Service):
    """DID Communication Service."""

    type: Literal["IndyAgent", "did-communication"] = "did-communication"
    recipient_keys: List[DIDUrl]
    routing_keys: List[DIDUrl] = []
    priority: int = 0
