"""
Type annotations for workspaces-thin-client service client paginators.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_workspaces_thin_client/paginators/)

Usage::

    ```python
    from boto3.session import Session

    from mypy_boto3_workspaces_thin_client.client import WorkSpacesThinClientClient
    from mypy_boto3_workspaces_thin_client.paginator import (
        ListDevicesPaginator,
        ListEnvironmentsPaginator,
        ListSoftwareSetsPaginator,
    )

    session = Session()
    client: WorkSpacesThinClientClient = session.client("workspaces-thin-client")

    list_devices_paginator: ListDevicesPaginator = client.get_paginator("list_devices")
    list_environments_paginator: ListEnvironmentsPaginator = client.get_paginator("list_environments")
    list_software_sets_paginator: ListSoftwareSetsPaginator = client.get_paginator("list_software_sets")
    ```
"""

from typing import Generic, Iterator, TypeVar

from botocore.paginate import PageIterator, Paginator

from .type_defs import (
    ListDevicesResponseTypeDef,
    ListEnvironmentsResponseTypeDef,
    ListSoftwareSetsResponseTypeDef,
    PaginatorConfigTypeDef,
)

__all__ = ("ListDevicesPaginator", "ListEnvironmentsPaginator", "ListSoftwareSetsPaginator")

_ItemTypeDef = TypeVar("_ItemTypeDef")


class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """


class ListDevicesPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/workspaces-thin-client.html#WorkSpacesThinClient.Paginator.ListDevices)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_workspaces_thin_client/paginators/#listdevicespaginator)
    """

    def paginate(
        self, *, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListDevicesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/workspaces-thin-client.html#WorkSpacesThinClient.Paginator.ListDevices.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_workspaces_thin_client/paginators/#listdevicespaginator)
        """


class ListEnvironmentsPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/workspaces-thin-client.html#WorkSpacesThinClient.Paginator.ListEnvironments)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_workspaces_thin_client/paginators/#listenvironmentspaginator)
    """

    def paginate(
        self, *, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListEnvironmentsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/workspaces-thin-client.html#WorkSpacesThinClient.Paginator.ListEnvironments.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_workspaces_thin_client/paginators/#listenvironmentspaginator)
        """


class ListSoftwareSetsPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/workspaces-thin-client.html#WorkSpacesThinClient.Paginator.ListSoftwareSets)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_workspaces_thin_client/paginators/#listsoftwaresetspaginator)
    """

    def paginate(
        self, *, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListSoftwareSetsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/workspaces-thin-client.html#WorkSpacesThinClient.Paginator.ListSoftwareSets.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_workspaces_thin_client/paginators/#listsoftwaresetspaginator)
        """
