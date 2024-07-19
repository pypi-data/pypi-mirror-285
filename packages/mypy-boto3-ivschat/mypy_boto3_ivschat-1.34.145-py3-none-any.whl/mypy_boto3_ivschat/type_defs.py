"""
Type annotations for ivschat service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_ivschat/type_defs/)

Usage::

    ```python
    from mypy_boto3_ivschat.type_defs import CloudWatchLogsDestinationConfigurationTypeDef

    data: CloudWatchLogsDestinationConfigurationTypeDef = ...
    ```
"""

import sys
from datetime import datetime
from typing import Dict, List, Mapping, Sequence

from .literals import ChatTokenCapabilityType, FallbackResultType, LoggingConfigurationStateType

if sys.version_info >= (3, 12):
    from typing import Literal
else:
    from typing_extensions import Literal
if sys.version_info >= (3, 12):
    from typing import NotRequired
else:
    from typing_extensions import NotRequired
if sys.version_info >= (3, 12):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

__all__ = (
    "CloudWatchLogsDestinationConfigurationTypeDef",
    "CreateChatTokenRequestRequestTypeDef",
    "ResponseMetadataTypeDef",
    "MessageReviewHandlerTypeDef",
    "DeleteLoggingConfigurationRequestRequestTypeDef",
    "DeleteMessageRequestRequestTypeDef",
    "DeleteRoomRequestRequestTypeDef",
    "FirehoseDestinationConfigurationTypeDef",
    "S3DestinationConfigurationTypeDef",
    "DisconnectUserRequestRequestTypeDef",
    "GetLoggingConfigurationRequestRequestTypeDef",
    "GetRoomRequestRequestTypeDef",
    "ListLoggingConfigurationsRequestRequestTypeDef",
    "ListRoomsRequestRequestTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "SendEventRequestRequestTypeDef",
    "TagResourceRequestRequestTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "CreateChatTokenResponseTypeDef",
    "DeleteMessageResponseTypeDef",
    "EmptyResponseMetadataTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "SendEventResponseTypeDef",
    "CreateRoomRequestRequestTypeDef",
    "CreateRoomResponseTypeDef",
    "GetRoomResponseTypeDef",
    "RoomSummaryTypeDef",
    "UpdateRoomRequestRequestTypeDef",
    "UpdateRoomResponseTypeDef",
    "DestinationConfigurationTypeDef",
    "ListRoomsResponseTypeDef",
    "CreateLoggingConfigurationRequestRequestTypeDef",
    "CreateLoggingConfigurationResponseTypeDef",
    "GetLoggingConfigurationResponseTypeDef",
    "LoggingConfigurationSummaryTypeDef",
    "UpdateLoggingConfigurationRequestRequestTypeDef",
    "UpdateLoggingConfigurationResponseTypeDef",
    "ListLoggingConfigurationsResponseTypeDef",
)

CloudWatchLogsDestinationConfigurationTypeDef = TypedDict(
    "CloudWatchLogsDestinationConfigurationTypeDef",
    {
        "logGroupName": str,
    },
)
CreateChatTokenRequestRequestTypeDef = TypedDict(
    "CreateChatTokenRequestRequestTypeDef",
    {
        "roomIdentifier": str,
        "userId": str,
        "capabilities": NotRequired[Sequence[ChatTokenCapabilityType]],
        "sessionDurationInMinutes": NotRequired[int],
        "attributes": NotRequired[Mapping[str, str]],
    },
)
ResponseMetadataTypeDef = TypedDict(
    "ResponseMetadataTypeDef",
    {
        "RequestId": str,
        "HTTPStatusCode": int,
        "HTTPHeaders": Dict[str, str],
        "RetryAttempts": int,
        "HostId": NotRequired[str],
    },
)
MessageReviewHandlerTypeDef = TypedDict(
    "MessageReviewHandlerTypeDef",
    {
        "uri": NotRequired[str],
        "fallbackResult": NotRequired[FallbackResultType],
    },
)
DeleteLoggingConfigurationRequestRequestTypeDef = TypedDict(
    "DeleteLoggingConfigurationRequestRequestTypeDef",
    {
        "identifier": str,
    },
)
DeleteMessageRequestRequestTypeDef = TypedDict(
    "DeleteMessageRequestRequestTypeDef",
    {
        "roomIdentifier": str,
        "id": str,
        "reason": NotRequired[str],
    },
)
DeleteRoomRequestRequestTypeDef = TypedDict(
    "DeleteRoomRequestRequestTypeDef",
    {
        "identifier": str,
    },
)
FirehoseDestinationConfigurationTypeDef = TypedDict(
    "FirehoseDestinationConfigurationTypeDef",
    {
        "deliveryStreamName": str,
    },
)
S3DestinationConfigurationTypeDef = TypedDict(
    "S3DestinationConfigurationTypeDef",
    {
        "bucketName": str,
    },
)
DisconnectUserRequestRequestTypeDef = TypedDict(
    "DisconnectUserRequestRequestTypeDef",
    {
        "roomIdentifier": str,
        "userId": str,
        "reason": NotRequired[str],
    },
)
GetLoggingConfigurationRequestRequestTypeDef = TypedDict(
    "GetLoggingConfigurationRequestRequestTypeDef",
    {
        "identifier": str,
    },
)
GetRoomRequestRequestTypeDef = TypedDict(
    "GetRoomRequestRequestTypeDef",
    {
        "identifier": str,
    },
)
ListLoggingConfigurationsRequestRequestTypeDef = TypedDict(
    "ListLoggingConfigurationsRequestRequestTypeDef",
    {
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ListRoomsRequestRequestTypeDef = TypedDict(
    "ListRoomsRequestRequestTypeDef",
    {
        "name": NotRequired[str],
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
        "messageReviewHandlerUri": NotRequired[str],
        "loggingConfigurationIdentifier": NotRequired[str],
    },
)
ListTagsForResourceRequestRequestTypeDef = TypedDict(
    "ListTagsForResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
    },
)
SendEventRequestRequestTypeDef = TypedDict(
    "SendEventRequestRequestTypeDef",
    {
        "roomIdentifier": str,
        "eventName": str,
        "attributes": NotRequired[Mapping[str, str]],
    },
)
TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "tags": Mapping[str, str],
    },
)
UntagResourceRequestRequestTypeDef = TypedDict(
    "UntagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "tagKeys": Sequence[str],
    },
)
CreateChatTokenResponseTypeDef = TypedDict(
    "CreateChatTokenResponseTypeDef",
    {
        "token": str,
        "tokenExpirationTime": datetime,
        "sessionExpirationTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteMessageResponseTypeDef = TypedDict(
    "DeleteMessageResponseTypeDef",
    {
        "id": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
EmptyResponseMetadataTypeDef = TypedDict(
    "EmptyResponseMetadataTypeDef",
    {
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListTagsForResourceResponseTypeDef = TypedDict(
    "ListTagsForResourceResponseTypeDef",
    {
        "tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
SendEventResponseTypeDef = TypedDict(
    "SendEventResponseTypeDef",
    {
        "id": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateRoomRequestRequestTypeDef = TypedDict(
    "CreateRoomRequestRequestTypeDef",
    {
        "name": NotRequired[str],
        "maximumMessageRatePerSecond": NotRequired[int],
        "maximumMessageLength": NotRequired[int],
        "messageReviewHandler": NotRequired[MessageReviewHandlerTypeDef],
        "tags": NotRequired[Mapping[str, str]],
        "loggingConfigurationIdentifiers": NotRequired[Sequence[str]],
    },
)
CreateRoomResponseTypeDef = TypedDict(
    "CreateRoomResponseTypeDef",
    {
        "arn": str,
        "id": str,
        "name": str,
        "createTime": datetime,
        "updateTime": datetime,
        "maximumMessageRatePerSecond": int,
        "maximumMessageLength": int,
        "messageReviewHandler": MessageReviewHandlerTypeDef,
        "tags": Dict[str, str],
        "loggingConfigurationIdentifiers": List[str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetRoomResponseTypeDef = TypedDict(
    "GetRoomResponseTypeDef",
    {
        "arn": str,
        "id": str,
        "name": str,
        "createTime": datetime,
        "updateTime": datetime,
        "maximumMessageRatePerSecond": int,
        "maximumMessageLength": int,
        "messageReviewHandler": MessageReviewHandlerTypeDef,
        "tags": Dict[str, str],
        "loggingConfigurationIdentifiers": List[str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
RoomSummaryTypeDef = TypedDict(
    "RoomSummaryTypeDef",
    {
        "arn": NotRequired[str],
        "id": NotRequired[str],
        "name": NotRequired[str],
        "messageReviewHandler": NotRequired[MessageReviewHandlerTypeDef],
        "createTime": NotRequired[datetime],
        "updateTime": NotRequired[datetime],
        "tags": NotRequired[Dict[str, str]],
        "loggingConfigurationIdentifiers": NotRequired[List[str]],
    },
)
UpdateRoomRequestRequestTypeDef = TypedDict(
    "UpdateRoomRequestRequestTypeDef",
    {
        "identifier": str,
        "name": NotRequired[str],
        "maximumMessageRatePerSecond": NotRequired[int],
        "maximumMessageLength": NotRequired[int],
        "messageReviewHandler": NotRequired[MessageReviewHandlerTypeDef],
        "loggingConfigurationIdentifiers": NotRequired[Sequence[str]],
    },
)
UpdateRoomResponseTypeDef = TypedDict(
    "UpdateRoomResponseTypeDef",
    {
        "arn": str,
        "id": str,
        "name": str,
        "createTime": datetime,
        "updateTime": datetime,
        "maximumMessageRatePerSecond": int,
        "maximumMessageLength": int,
        "messageReviewHandler": MessageReviewHandlerTypeDef,
        "tags": Dict[str, str],
        "loggingConfigurationIdentifiers": List[str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DestinationConfigurationTypeDef = TypedDict(
    "DestinationConfigurationTypeDef",
    {
        "s3": NotRequired[S3DestinationConfigurationTypeDef],
        "cloudWatchLogs": NotRequired[CloudWatchLogsDestinationConfigurationTypeDef],
        "firehose": NotRequired[FirehoseDestinationConfigurationTypeDef],
    },
)
ListRoomsResponseTypeDef = TypedDict(
    "ListRoomsResponseTypeDef",
    {
        "rooms": List[RoomSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateLoggingConfigurationRequestRequestTypeDef = TypedDict(
    "CreateLoggingConfigurationRequestRequestTypeDef",
    {
        "destinationConfiguration": DestinationConfigurationTypeDef,
        "name": NotRequired[str],
        "tags": NotRequired[Mapping[str, str]],
    },
)
CreateLoggingConfigurationResponseTypeDef = TypedDict(
    "CreateLoggingConfigurationResponseTypeDef",
    {
        "arn": str,
        "id": str,
        "createTime": datetime,
        "updateTime": datetime,
        "name": str,
        "destinationConfiguration": DestinationConfigurationTypeDef,
        "state": Literal["ACTIVE"],
        "tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetLoggingConfigurationResponseTypeDef = TypedDict(
    "GetLoggingConfigurationResponseTypeDef",
    {
        "arn": str,
        "id": str,
        "createTime": datetime,
        "updateTime": datetime,
        "name": str,
        "destinationConfiguration": DestinationConfigurationTypeDef,
        "state": LoggingConfigurationStateType,
        "tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
LoggingConfigurationSummaryTypeDef = TypedDict(
    "LoggingConfigurationSummaryTypeDef",
    {
        "arn": NotRequired[str],
        "id": NotRequired[str],
        "createTime": NotRequired[datetime],
        "updateTime": NotRequired[datetime],
        "name": NotRequired[str],
        "destinationConfiguration": NotRequired[DestinationConfigurationTypeDef],
        "state": NotRequired[LoggingConfigurationStateType],
        "tags": NotRequired[Dict[str, str]],
    },
)
UpdateLoggingConfigurationRequestRequestTypeDef = TypedDict(
    "UpdateLoggingConfigurationRequestRequestTypeDef",
    {
        "identifier": str,
        "name": NotRequired[str],
        "destinationConfiguration": NotRequired[DestinationConfigurationTypeDef],
    },
)
UpdateLoggingConfigurationResponseTypeDef = TypedDict(
    "UpdateLoggingConfigurationResponseTypeDef",
    {
        "arn": str,
        "id": str,
        "createTime": datetime,
        "updateTime": datetime,
        "name": str,
        "destinationConfiguration": DestinationConfigurationTypeDef,
        "state": Literal["ACTIVE"],
        "tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListLoggingConfigurationsResponseTypeDef = TypedDict(
    "ListLoggingConfigurationsResponseTypeDef",
    {
        "loggingConfigurations": List[LoggingConfigurationSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
