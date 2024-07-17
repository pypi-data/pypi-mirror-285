import datetime
from abc import ABC
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Dict, List, Optional

from dataclass_wizard import JSONSerializable


@dataclass
class Error(JSONSerializable):
    code: int | None = None
    message: str | None = None


@dataclass
class NBFunctions:
    function_name: str | None = field(default_factory=str)
    function_code: str | None = field(default_factory=str)


@dataclass
class ParsedNBModel:
    nbpython_version: str | None = field(default_factory=str)
    nbfunctions: List[NBFunctions] = field(default_factory=list)


@dataclass
class RequestResponse(JSONSerializable, ABC):
    status_code: int | None = None
    error: Error | None = None


@dataclass
class RequestResponseGeneric(RequestResponse):
    data: Dict[str, Any] | str | None = None


@dataclass
class RequestResponseForModel(RequestResponse):
    data: ParsedNBModel = field(default_factory=ParsedNBModel)


@dataclass
class NotebookInfo(JSONSerializable):
    functionName: str = field(default_factory=str)
    functionCode: str = field(default_factory=str)
    description: str = field(default_factory=str)
    notebookName: str = field(default_factory=str)
    owner: str = field(default_factory=str)
    nbPath: str = field(default_factory=str)


@dataclass
class ImageCreationJob:
    id: int = field(default_factory=int)
    jobId: str = field(default_factory=str)
    stage: str = field(default_factory=str)
    status: str = field(default_factory=str)
    reason: str = field(default_factory=str)
    trace: str = field(default_factory=str)

@dataclass
class FunctionParameters(JSONSerializable):
    id: str = field(default_factory=str)
    name: str = field(default_factory=str)
    type: str = field(default_factory=str)
    description: str = field(default_factory=str)


@dataclass
class EndpointVersion(JSONSerializable):
    id: int = field(default_factory=int)
    versionName: str = field(default_factory=str)
    description: str = field(default_factory=str)
    isActive: bool = field(default_factory=bool)
    shortHash: str = field(default_factory=str)
    status: str = field(default_factory=str)
    createdAt: datetime.datetime = field(default_factory=datetime.datetime.now)
    updatedAt: datetime.datetime = field(default_factory=datetime.datetime.now)
    jobs: Optional[list[ImageCreationJob]] = field(
        default_factory=list[ImageCreationJob]
    )
    parameters: Optional[list[FunctionParameters]] = field(
        default_factory=list[FunctionParameters]
    )


@dataclass
class APIKey(JSONSerializable):
    id: int = field(default_factory=int)
    apiKeyName: str = field(default_factory=str)
    description: str = field(default_factory=str)
    apiKey: str = field(default_factory=str)
    createdAt: datetime.datetime = field(default_factory=datetime.datetime.now)
    updatedAt: datetime.datetime = field(default_factory=datetime.datetime.now)
    expiresAt: datetime.datetime = field(default_factory=datetime.datetime.now)
    isActive: bool = field(default_factory=bool)
    refreshCount: int = field(default_factory=int)


@dataclass
class Endpoint(JSONSerializable):
    id: int = field(default_factory=int)
    functionName: str = field(default_factory=str)
    description: str = field(default_factory=str)
    notebookName: str = field(default_factory=str)
    owner: str = field(default_factory=str)
    createdAt: datetime.datetime = field(default_factory=datetime.datetime.now)
    updatedAt: datetime.datetime = field(default_factory=datetime.datetime.now)
    filesPath: str = field(default_factory=str)
    versions: Optional[list[EndpointVersion]] = field(
        default_factory=list[EndpointVersion]
    )
    apiKeys: Optional[list[APIKey]] = field(default_factory=list[APIKey])


@dataclass
class EndpointResponse(RequestResponse):
    data: Endpoint = field(default_factory=Endpoint)

@dataclass
class EndpointVersionResponse(RequestResponse):
    data: EndpointVersion = field(default_factory=EndpointVersion)


@dataclass
class EndpointListResponse(RequestResponse):
    data: list[Endpoint] = field(default_factory=list[Endpoint])


@dataclass
class JLCreateEndpointResponse(EndpointResponse):
    message: str = field(default_factory=str)


@dataclass
class EndpointUpdatesInterface:
    owner: str = field(default_factory=str)
    version: str = field(default_factory=str)
    versionName: str = field(default_factory=str)
    action: str = field(default_factory=str)
    id: int = field(default_factory=int)


@dataclass
class OwnerRequest:
    owner: str = field(default_factory=str)




class APIKeyType(IntEnum):
    USER = 1
    ADMIN = 2


@dataclass
class CreateAPIKeyRequest:
    current_user: str = field(default_factory=str)
    endpoint_id: int = field(default_factory=int)
    name: str = field(default_factory=str)
    description: str = field(default_factory=str)

@dataclass
class UpdateAPIKeyRequest:
    current_user: str = field(default_factory=str)
    endpoint_id: int = field(default_factory=int)
    api_key_id: int = field(default_factory=int)
    name: str = field(default_factory=str)
    description: str = field(default_factory=str)

@dataclass
class DeleteVersionRequest:
    current_user: str = field(default_factory=str)
    endpoint_id: int = field(default_factory=int)
    version_id: int = field(default_factory=int)

@dataclass
class EndpointIdRequest:
    id: int = field(default_factory=int)
