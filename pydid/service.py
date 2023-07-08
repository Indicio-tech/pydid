"""DID Doc Service."""

from typing import List, Optional, Union

from pydantic import Extra, AnyUrl
from typing_extensions import Literal

from .did_url import DIDUrl
from .resource import Resource


class ServiceEndpoint(Resource):
    """List of Service Endpoints"""

    uri: Union[DIDUrl, AnyUrl]


class Service(Resource):
    """Representation of DID Document Services."""

    id: DIDUrl
    type: str
    service_endpoint: Union[DIDUrl, AnyUrl, Literal[""], List[ServiceEndpoint]]


class DIDCommV1Service(Service):
    """DID Communication Service."""

    class Config:
        """DIDComm Service Config."""

        extra = Extra.forbid

    type: Literal[
        "IndyAgent", "did-communication", "DIDCommMessaging"
    ] = "did-communication"
    recipient_keys: List[DIDUrl]
    routing_keys: List[DIDUrl] = []
    accept: Optional[List[str]] = None
    priority: int = 0


DIDCommService = DIDCommV1Service


class DIDCommV2ServiceEndpoint(ServiceEndpoint):
    """DID Communication Service Endpoint."""

    uri: Union[DIDUrl, AnyUrl]
    accept: Optional[List[str]] = None
    routing_keys: List[DIDUrl] = []


class DIDCommV2Service(Service):
    """DID Communication V2 Service."""

    class Config:
        """DIDComm Service Config."""

        extra = Extra.forbid

    type: Literal["DIDCommMessaging"] = "DIDCommMessaging"
    service_endpoint: List[DIDCommV2ServiceEndpoint]


class UnknownService(Service):
    """Unknown Service."""
