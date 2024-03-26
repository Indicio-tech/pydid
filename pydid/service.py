"""DID Doc Service."""

from typing import Any, List, Mapping, Optional, Union

from pydantic import AnyUrl, ConfigDict, StrictStr
from typing_extensions import Literal

from .did import DID
from .did_url import DIDUrl
from .resource import Resource

EndpointStrings = Union[DID, DIDUrl, AnyUrl, StrictStr]


class Service(Resource):
    """Representation of DID Document Services."""

    id: DIDUrl
    type: Union[str, List[str]]
    service_endpoint: Union[
        EndpointStrings,
        List[Union[EndpointStrings, Mapping[str, Any]]],
        Mapping[str, Any],
    ]


class DIDCommV1Service(Service):
    """DID Communication Service."""

    model_config = ConfigDict(extra="forbid")

    type: Literal["IndyAgent", "did-communication", "DIDCommMessaging"] = (
        "did-communication"
    )
    service_endpoint: EndpointStrings
    recipient_keys: List[DIDUrl]
    routing_keys: List[DIDUrl] = []
    accept: Optional[List[str]] = None
    priority: int = 0


DIDCommService = DIDCommV1Service


class DIDCommV2ServiceEndpoint(Resource):
    """DID Communication Service Endpoint."""

    uri: EndpointStrings
    accept: Optional[List[str]] = None
    routing_keys: List[DIDUrl] = []


class DIDCommV2Service(Service):
    """DID Communication V2 Service."""

    model_config = ConfigDict(extra="forbid")

    type: Literal["DIDCommMessaging"] = "DIDCommMessaging"
    service_endpoint: Union[List[DIDCommV2ServiceEndpoint], DIDCommV2ServiceEndpoint]


class UnknownService(Service):
    """Unknown Service."""
