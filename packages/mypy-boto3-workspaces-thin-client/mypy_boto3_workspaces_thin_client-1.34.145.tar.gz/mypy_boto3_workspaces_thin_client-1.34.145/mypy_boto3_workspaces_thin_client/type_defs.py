"""
Type annotations for workspaces-thin-client service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_workspaces_thin_client/type_defs/)

Usage::

    ```python
    from mypy_boto3_workspaces_thin_client.type_defs import MaintenanceWindowTypeDef

    data: MaintenanceWindowTypeDef = ...
    ```
"""

import sys
from datetime import datetime
from typing import Dict, List, Mapping, Sequence, Union

from .literals import (
    ApplyTimeOfType,
    DayOfWeekType,
    DesktopTypeType,
    DeviceSoftwareSetComplianceStatusType,
    DeviceStatusType,
    EnvironmentSoftwareSetComplianceStatusType,
    MaintenanceWindowTypeType,
    SoftwareSetUpdateModeType,
    SoftwareSetUpdateScheduleType,
    SoftwareSetUpdateStatusType,
    SoftwareSetValidationStatusType,
    TargetDeviceStatusType,
)

if sys.version_info >= (3, 12):
    from typing import NotRequired
else:
    from typing_extensions import NotRequired
if sys.version_info >= (3, 12):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

__all__ = (
    "MaintenanceWindowTypeDef",
    "ResponseMetadataTypeDef",
    "DeleteDeviceRequestRequestTypeDef",
    "DeleteEnvironmentRequestRequestTypeDef",
    "DeregisterDeviceRequestRequestTypeDef",
    "DeviceSummaryTypeDef",
    "DeviceTypeDef",
    "MaintenanceWindowOutputTypeDef",
    "GetDeviceRequestRequestTypeDef",
    "GetEnvironmentRequestRequestTypeDef",
    "GetSoftwareSetRequestRequestTypeDef",
    "PaginatorConfigTypeDef",
    "ListDevicesRequestRequestTypeDef",
    "ListEnvironmentsRequestRequestTypeDef",
    "ListSoftwareSetsRequestRequestTypeDef",
    "SoftwareSetSummaryTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "MaintenanceWindowExtraOutputTypeDef",
    "SoftwareTypeDef",
    "TagResourceRequestRequestTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "UpdateDeviceRequestRequestTypeDef",
    "UpdateSoftwareSetRequestRequestTypeDef",
    "CreateEnvironmentRequestRequestTypeDef",
    "UpdateEnvironmentRequestRequestTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "ListDevicesResponseTypeDef",
    "UpdateDeviceResponseTypeDef",
    "GetDeviceResponseTypeDef",
    "EnvironmentSummaryTypeDef",
    "EnvironmentTypeDef",
    "ListDevicesRequestListDevicesPaginateTypeDef",
    "ListEnvironmentsRequestListEnvironmentsPaginateTypeDef",
    "ListSoftwareSetsRequestListSoftwareSetsPaginateTypeDef",
    "ListSoftwareSetsResponseTypeDef",
    "MaintenanceWindowUnionTypeDef",
    "SoftwareSetTypeDef",
    "CreateEnvironmentResponseTypeDef",
    "ListEnvironmentsResponseTypeDef",
    "UpdateEnvironmentResponseTypeDef",
    "GetEnvironmentResponseTypeDef",
    "GetSoftwareSetResponseTypeDef",
)

MaintenanceWindowTypeDef = TypedDict(
    "MaintenanceWindowTypeDef",
    {
        "type": NotRequired[MaintenanceWindowTypeType],
        "startTimeHour": NotRequired[int],
        "startTimeMinute": NotRequired[int],
        "endTimeHour": NotRequired[int],
        "endTimeMinute": NotRequired[int],
        "daysOfTheWeek": NotRequired[Sequence[DayOfWeekType]],
        "applyTimeOf": NotRequired[ApplyTimeOfType],
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
DeleteDeviceRequestRequestTypeDef = TypedDict(
    "DeleteDeviceRequestRequestTypeDef",
    {
        "id": str,
        "clientToken": NotRequired[str],
    },
)
DeleteEnvironmentRequestRequestTypeDef = TypedDict(
    "DeleteEnvironmentRequestRequestTypeDef",
    {
        "id": str,
        "clientToken": NotRequired[str],
    },
)
DeregisterDeviceRequestRequestTypeDef = TypedDict(
    "DeregisterDeviceRequestRequestTypeDef",
    {
        "id": str,
        "targetDeviceStatus": NotRequired[TargetDeviceStatusType],
        "clientToken": NotRequired[str],
    },
)
DeviceSummaryTypeDef = TypedDict(
    "DeviceSummaryTypeDef",
    {
        "id": NotRequired[str],
        "serialNumber": NotRequired[str],
        "name": NotRequired[str],
        "model": NotRequired[str],
        "environmentId": NotRequired[str],
        "status": NotRequired[DeviceStatusType],
        "currentSoftwareSetId": NotRequired[str],
        "desiredSoftwareSetId": NotRequired[str],
        "pendingSoftwareSetId": NotRequired[str],
        "softwareSetUpdateSchedule": NotRequired[SoftwareSetUpdateScheduleType],
        "lastConnectedAt": NotRequired[datetime],
        "lastPostureAt": NotRequired[datetime],
        "createdAt": NotRequired[datetime],
        "updatedAt": NotRequired[datetime],
        "arn": NotRequired[str],
    },
)
DeviceTypeDef = TypedDict(
    "DeviceTypeDef",
    {
        "id": NotRequired[str],
        "serialNumber": NotRequired[str],
        "name": NotRequired[str],
        "model": NotRequired[str],
        "environmentId": NotRequired[str],
        "status": NotRequired[DeviceStatusType],
        "currentSoftwareSetId": NotRequired[str],
        "currentSoftwareSetVersion": NotRequired[str],
        "desiredSoftwareSetId": NotRequired[str],
        "pendingSoftwareSetId": NotRequired[str],
        "pendingSoftwareSetVersion": NotRequired[str],
        "softwareSetUpdateSchedule": NotRequired[SoftwareSetUpdateScheduleType],
        "softwareSetComplianceStatus": NotRequired[DeviceSoftwareSetComplianceStatusType],
        "softwareSetUpdateStatus": NotRequired[SoftwareSetUpdateStatusType],
        "lastConnectedAt": NotRequired[datetime],
        "lastPostureAt": NotRequired[datetime],
        "createdAt": NotRequired[datetime],
        "updatedAt": NotRequired[datetime],
        "arn": NotRequired[str],
        "kmsKeyArn": NotRequired[str],
        "tags": NotRequired[Dict[str, str]],
    },
)
MaintenanceWindowOutputTypeDef = TypedDict(
    "MaintenanceWindowOutputTypeDef",
    {
        "type": NotRequired[MaintenanceWindowTypeType],
        "startTimeHour": NotRequired[int],
        "startTimeMinute": NotRequired[int],
        "endTimeHour": NotRequired[int],
        "endTimeMinute": NotRequired[int],
        "daysOfTheWeek": NotRequired[List[DayOfWeekType]],
        "applyTimeOf": NotRequired[ApplyTimeOfType],
    },
)
GetDeviceRequestRequestTypeDef = TypedDict(
    "GetDeviceRequestRequestTypeDef",
    {
        "id": str,
    },
)
GetEnvironmentRequestRequestTypeDef = TypedDict(
    "GetEnvironmentRequestRequestTypeDef",
    {
        "id": str,
    },
)
GetSoftwareSetRequestRequestTypeDef = TypedDict(
    "GetSoftwareSetRequestRequestTypeDef",
    {
        "id": str,
    },
)
PaginatorConfigTypeDef = TypedDict(
    "PaginatorConfigTypeDef",
    {
        "MaxItems": NotRequired[int],
        "PageSize": NotRequired[int],
        "StartingToken": NotRequired[str],
    },
)
ListDevicesRequestRequestTypeDef = TypedDict(
    "ListDevicesRequestRequestTypeDef",
    {
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ListEnvironmentsRequestRequestTypeDef = TypedDict(
    "ListEnvironmentsRequestRequestTypeDef",
    {
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ListSoftwareSetsRequestRequestTypeDef = TypedDict(
    "ListSoftwareSetsRequestRequestTypeDef",
    {
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
SoftwareSetSummaryTypeDef = TypedDict(
    "SoftwareSetSummaryTypeDef",
    {
        "id": NotRequired[str],
        "version": NotRequired[str],
        "releasedAt": NotRequired[datetime],
        "supportedUntil": NotRequired[datetime],
        "validationStatus": NotRequired[SoftwareSetValidationStatusType],
        "arn": NotRequired[str],
    },
)
ListTagsForResourceRequestRequestTypeDef = TypedDict(
    "ListTagsForResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
    },
)
MaintenanceWindowExtraOutputTypeDef = TypedDict(
    "MaintenanceWindowExtraOutputTypeDef",
    {
        "type": NotRequired[MaintenanceWindowTypeType],
        "startTimeHour": NotRequired[int],
        "startTimeMinute": NotRequired[int],
        "endTimeHour": NotRequired[int],
        "endTimeMinute": NotRequired[int],
        "daysOfTheWeek": NotRequired[List[DayOfWeekType]],
        "applyTimeOf": NotRequired[ApplyTimeOfType],
    },
)
SoftwareTypeDef = TypedDict(
    "SoftwareTypeDef",
    {
        "name": NotRequired[str],
        "version": NotRequired[str],
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
UpdateDeviceRequestRequestTypeDef = TypedDict(
    "UpdateDeviceRequestRequestTypeDef",
    {
        "id": str,
        "name": NotRequired[str],
        "desiredSoftwareSetId": NotRequired[str],
        "softwareSetUpdateSchedule": NotRequired[SoftwareSetUpdateScheduleType],
    },
)
UpdateSoftwareSetRequestRequestTypeDef = TypedDict(
    "UpdateSoftwareSetRequestRequestTypeDef",
    {
        "id": str,
        "validationStatus": SoftwareSetValidationStatusType,
    },
)
CreateEnvironmentRequestRequestTypeDef = TypedDict(
    "CreateEnvironmentRequestRequestTypeDef",
    {
        "desktopArn": str,
        "name": NotRequired[str],
        "desktopEndpoint": NotRequired[str],
        "softwareSetUpdateSchedule": NotRequired[SoftwareSetUpdateScheduleType],
        "maintenanceWindow": NotRequired[MaintenanceWindowTypeDef],
        "softwareSetUpdateMode": NotRequired[SoftwareSetUpdateModeType],
        "desiredSoftwareSetId": NotRequired[str],
        "kmsKeyArn": NotRequired[str],
        "clientToken": NotRequired[str],
        "tags": NotRequired[Mapping[str, str]],
        "deviceCreationTags": NotRequired[Mapping[str, str]],
    },
)
UpdateEnvironmentRequestRequestTypeDef = TypedDict(
    "UpdateEnvironmentRequestRequestTypeDef",
    {
        "id": str,
        "name": NotRequired[str],
        "desktopArn": NotRequired[str],
        "desktopEndpoint": NotRequired[str],
        "softwareSetUpdateSchedule": NotRequired[SoftwareSetUpdateScheduleType],
        "maintenanceWindow": NotRequired[MaintenanceWindowTypeDef],
        "softwareSetUpdateMode": NotRequired[SoftwareSetUpdateModeType],
        "desiredSoftwareSetId": NotRequired[str],
        "deviceCreationTags": NotRequired[Mapping[str, str]],
    },
)
ListTagsForResourceResponseTypeDef = TypedDict(
    "ListTagsForResourceResponseTypeDef",
    {
        "tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListDevicesResponseTypeDef = TypedDict(
    "ListDevicesResponseTypeDef",
    {
        "devices": List[DeviceSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateDeviceResponseTypeDef = TypedDict(
    "UpdateDeviceResponseTypeDef",
    {
        "device": DeviceSummaryTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetDeviceResponseTypeDef = TypedDict(
    "GetDeviceResponseTypeDef",
    {
        "device": DeviceTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
EnvironmentSummaryTypeDef = TypedDict(
    "EnvironmentSummaryTypeDef",
    {
        "id": NotRequired[str],
        "name": NotRequired[str],
        "desktopArn": NotRequired[str],
        "desktopEndpoint": NotRequired[str],
        "desktopType": NotRequired[DesktopTypeType],
        "activationCode": NotRequired[str],
        "softwareSetUpdateSchedule": NotRequired[SoftwareSetUpdateScheduleType],
        "maintenanceWindow": NotRequired[MaintenanceWindowOutputTypeDef],
        "softwareSetUpdateMode": NotRequired[SoftwareSetUpdateModeType],
        "desiredSoftwareSetId": NotRequired[str],
        "pendingSoftwareSetId": NotRequired[str],
        "createdAt": NotRequired[datetime],
        "updatedAt": NotRequired[datetime],
        "arn": NotRequired[str],
    },
)
EnvironmentTypeDef = TypedDict(
    "EnvironmentTypeDef",
    {
        "id": NotRequired[str],
        "name": NotRequired[str],
        "desktopArn": NotRequired[str],
        "desktopEndpoint": NotRequired[str],
        "desktopType": NotRequired[DesktopTypeType],
        "activationCode": NotRequired[str],
        "registeredDevicesCount": NotRequired[int],
        "softwareSetUpdateSchedule": NotRequired[SoftwareSetUpdateScheduleType],
        "maintenanceWindow": NotRequired[MaintenanceWindowOutputTypeDef],
        "softwareSetUpdateMode": NotRequired[SoftwareSetUpdateModeType],
        "desiredSoftwareSetId": NotRequired[str],
        "pendingSoftwareSetId": NotRequired[str],
        "pendingSoftwareSetVersion": NotRequired[str],
        "softwareSetComplianceStatus": NotRequired[EnvironmentSoftwareSetComplianceStatusType],
        "createdAt": NotRequired[datetime],
        "updatedAt": NotRequired[datetime],
        "arn": NotRequired[str],
        "kmsKeyArn": NotRequired[str],
        "tags": NotRequired[Dict[str, str]],
        "deviceCreationTags": NotRequired[Dict[str, str]],
    },
)
ListDevicesRequestListDevicesPaginateTypeDef = TypedDict(
    "ListDevicesRequestListDevicesPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListEnvironmentsRequestListEnvironmentsPaginateTypeDef = TypedDict(
    "ListEnvironmentsRequestListEnvironmentsPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListSoftwareSetsRequestListSoftwareSetsPaginateTypeDef = TypedDict(
    "ListSoftwareSetsRequestListSoftwareSetsPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListSoftwareSetsResponseTypeDef = TypedDict(
    "ListSoftwareSetsResponseTypeDef",
    {
        "softwareSets": List[SoftwareSetSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
MaintenanceWindowUnionTypeDef = Union[MaintenanceWindowTypeDef, MaintenanceWindowExtraOutputTypeDef]
SoftwareSetTypeDef = TypedDict(
    "SoftwareSetTypeDef",
    {
        "id": NotRequired[str],
        "version": NotRequired[str],
        "releasedAt": NotRequired[datetime],
        "supportedUntil": NotRequired[datetime],
        "validationStatus": NotRequired[SoftwareSetValidationStatusType],
        "software": NotRequired[List[SoftwareTypeDef]],
        "arn": NotRequired[str],
        "tags": NotRequired[Dict[str, str]],
    },
)
CreateEnvironmentResponseTypeDef = TypedDict(
    "CreateEnvironmentResponseTypeDef",
    {
        "environment": EnvironmentSummaryTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListEnvironmentsResponseTypeDef = TypedDict(
    "ListEnvironmentsResponseTypeDef",
    {
        "environments": List[EnvironmentSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateEnvironmentResponseTypeDef = TypedDict(
    "UpdateEnvironmentResponseTypeDef",
    {
        "environment": EnvironmentSummaryTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetEnvironmentResponseTypeDef = TypedDict(
    "GetEnvironmentResponseTypeDef",
    {
        "environment": EnvironmentTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetSoftwareSetResponseTypeDef = TypedDict(
    "GetSoftwareSetResponseTypeDef",
    {
        "softwareSet": SoftwareSetTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
