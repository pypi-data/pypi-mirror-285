from typing import Optional, List, Tuple

import typer
from thestage_core.services.clients.thestage_api.api_client import TheStageApiClientCore

from thestage.config import THESTAGE_API_URL
from thestage.services.clients.thestage_api.dtos.enums.selfhosted_status import SelfHostedStatusEnumDto, \
    SelfHostedBusinessStatusEnumDto
from thestage.services.clients.thestage_api.dtos.selfhosted_instance_response import SelfHostedInstanceListResponse, \
    SelfHostedInstanceDto, SelfHostedRentedItemResponse
from thestage.services.clients.thestage_api.dtos.container_param_request import DockerContainerCreateRequestDto, \
    DockerContainerActionRequestDto
from thestage.services.clients.thestage_api.dtos.container_response import DockerContainerListResponse, DockerContainerDto, \
    DockerContainerItemResponse
from thestage.services.clients.thestage_api.dtos.enums.container_status import ContainerStatusEnumDto
from thestage.entities.enums.order_direction_type import OrderDirectionType
from thestage.services.clients.thestage_api.dtos.user_profile import UserProfileResponse
from thestage.services.clients.thestage_api.dtos.enums.rented_status import RentedStatusEnumDto, \
    RentedBusinessStatusEnumDto
from thestage.services.clients.thestage_api.dtos.instance_rented_response import InstanceRentedListResponse, \
    InstanceRentedDto, InstanceRentedItemResponse
from thestage.services.clients.thestage_api.dtos.sketch_response import SketchViewResponse, SketchDto, SketchRunTaskResponse
from thestage.services.clients.thestage_api.dtos.storage_rented_response import StorageRentedListResponse, StorageRentedDto
from thestage.services.clients.thestage_api.dtos.task_response import TaskViewResponse, TaskDto, TaskListForSketchResponse, \
    TaskListForSketchPaging, TaskGetOutputResponse
from thestage.services.clients.thestage_api.dtos.base_response import TheStageBaseResponse, TheStageBasePaginatedResponse


class TheStageApiClient(TheStageApiClientCore):

    def __init__(self, timeout: int = 90):
        super(TheStageApiClient, self).__init__(timeout=timeout)

    def _get_host(self, ) -> str:
        return THESTAGE_API_URL

    def get_sketch_by_slug(self, slug: str, token: str) -> Optional[SketchDto]:
        data = {
            "sketchSlug": slug,
        }

        response = self._request(
            method='POST',
            url='/user-api/v1/sketch/view-by-slug',
            data=data,
            token=token,
        )

        result = SketchViewResponse.model_validate(response) if response else None
        return result.sketch if result and result.is_success else None

    def execute_run_task(
            self,
            token: str,
            sketch_slug: str,
            instance_rented_slug: str,
            storage_rented_slug: str,
            run_command: str,
            run_args: str,
            task_title: str,
            commit_hash: Optional[str] = None,
            task_description: Optional[str] = None,
    ) -> Optional[SketchRunTaskResponse]:
        data = {
            "sketchSlug": sketch_slug,
            "instanceRentedSlug": instance_rented_slug,
            "storageRentedSlug": storage_rented_slug,
            "commitHash": commit_hash,
            "runCommand": run_command,
            "runArgs": run_args,
            "taskTitle": task_title,
            "taskDescription": task_description,
        }

        response = self._request(
            method='POST',
            url='/user-api/v1/sketch/execute-task',
            data=data,
            token=token,
        )

        return SketchRunTaskResponse.model_validate(response) if response else None

    def get_task_info_by_task_id(
            self,
            token: str,
            task_id: int,
    ) -> Optional[TaskViewResponse]:
        data = {
            "taskId": task_id,
        }

        response = self._request(
            method='POST',
            url='/user-api/v1/task/view',
            data=data,
            token=token,
        )

        result = TaskViewResponse.model_validate(response) if response else None
        return result if result and result.is_success else None

    def get_task_list_by_sketch(
            self,
            token: str,
            sketch_slug: str,
            page: int = 1,
            limit: int = 10,
            order_directions: OrderDirectionType = OrderDirectionType.DESC,
    ) -> Optional[TaskListForSketchPaging]:
        data = {
            "entityFilterRequest": {
                "orderByField": "id",
                "orderByDirection": order_directions.value,
                "page": page,
                "limit": limit,
            },
            "sketchSlug": sketch_slug
        }

        response = self._request(
            method='POST',
            url='/user-api/v1/task/list-for-sketch',
            data=data,
            token=token,
        )

        result = TaskListForSketchResponse.model_validate(response) if response else None
        return result.tasks if result and result.is_success else None

    def get_output_task(
            self,
            token: str,
            task_id: int,
    ) -> Optional[TaskGetOutputResponse]:
        data = {
            "taskId": task_id,
        }

        response = self._request(
            method='POST',
            url='/user-api/v1/task/get-output',
            data=data,
            token=token,
        )

        result = TaskGetOutputResponse.model_validate(response) if response else None
        return result if result else None

    def get_rented_storage_list(
            self,
            token: str,
            statuses: List[RentedStatusEnumDto],
            query: Optional[str] = None,
            page: int = 1,
            limit: int = 10,
    ) -> Tuple[List[StorageRentedDto], int]:

        data = {
            #"statuses": [item.value for item in statuses] if statuses else [],
            "entityFilterRequest": {
                "orderByField": "id",
                "orderByDirection": "DESC",
                "page": page,
                "limit": limit
            },
            "queryString": query
        }

        if statuses:
            data['statuses'] = [item.value for item in statuses] if statuses else []

        response = self._request(
            method='POST',
            url='/user-api/v1/storage-rented/list',
            data=data,
            token=token,
        )

        result = StorageRentedListResponse.model_validate(response) if response else None
        return (result.entities, result.pagination_data.total_pages) if result else ([], None)

    def get_rented_instance_list(
            self,
            token: str,
            statuses: List[RentedBusinessStatusEnumDto],
            query: Optional[str] = None,
            page: int = 1,
            limit: int = 10,
    ) -> Tuple[List[InstanceRentedDto], int]:
        data = {
            #"statuses": [item.value for item in statuses],
            "entityFilterRequest": {
                "orderByField": "id",
                "orderByDirection": "DESC",
                "page": page,
                "limit": limit
            },
            "queryString": query
        }

        if statuses:
            data['businessStatuses'] = [item.value for item in statuses]

        response = self._request(
            method='POST',
            url='/user-api/v1/instance-rented/list',
            data=data,
            token=token,
        )

        result = InstanceRentedListResponse.model_validate(response) if response else None
        return (result.paginated_list.entities, result.paginated_list.pagination_data.total_pages) if result and result.paginated_list else ([], None)

    def get_rented_business_status_map(self, token: str,) -> None:
        response = self._request(
            method='POST',
            url='/user-api/instance-rented/business-status-localized-map',
            data=None,
            token=token,
        )

        return InstanceRentedItemResponse.model_validate(response).instance_rented if response else None

    def get_rented_item(
            self,
            token: str,
            instance_slug: Optional[str] = None,
            instance_id: Optional[int] = None,
    ) -> Optional[InstanceRentedDto]:
        if not instance_slug and not instance_id:
            return None

        data = {
            "instanceRentedSlug": instance_slug,
        }

        response = self._request(
            method='POST',
            url='/user-api/v1/instance-rented/view-by-slug',
            data=data,
            token=token,
        )

        return InstanceRentedItemResponse.model_validate(response).instance_rented if response else None

    def get_selfhosted_item(
            self,
            token: str,
            instance_slug: Optional[str] = None,
            instance_id: Optional[int] = None,
    ) -> Optional[SelfHostedInstanceDto]:
        if not instance_slug and not instance_id:
            return None

        data = {
            "selfhostedInstanceSlug": instance_slug,
        }

        response = self._request(
            method='POST',
            url='/user-api/v1/self-hosted-instance/view-by-slug',
            data=data,
            token=token,
        )

        return SelfHostedRentedItemResponse.model_validate(response).selfhosted_instance if response else None

    def get_selfhosted_instance_list(
            self,
            token: str,
            statuses: List[SelfHostedBusinessStatusEnumDto],
            query: Optional[str] = None,
            page: int = 1,
            limit: int = 10,
    ) -> Tuple[List[SelfHostedInstanceDto], int]:
        data = {
            #"statuses": [item.value for item in statuses] if statuses else [],
            "entityFilterRequest": {
                "orderByField": "id",
                "orderByDirection": "DESC",
                "page": page,
                "limit": limit
            },
            "queryString": query
        }

        if statuses:
            data['businessStatuses'] = [item.value for item in statuses]

        response = self._request(
            method='POST',
            url='/user-api/v1/self-hosted-instance/list',
            data=data,
            token=token,
        )

        result = SelfHostedInstanceListResponse.model_validate(response) if response else None
        return (result.paginated_list.entities, result.paginated_list.pagination_data.total_pages) if result and result.paginated_list else ([], None)

    def get_selfhosted_business_status_map(self, token: str,) -> None:
        response = self._request(
            method='POST',
            url='/user-api/self-hosted-instance/business-status-localized-map',
            data=None,
            token=token,
        )

        return InstanceRentedItemResponse.model_validate(response).instance_rented if response else None

    def get_profile(
            self,
            token: str,
    ) -> Optional[UserProfileResponse]:

        response = self._request(
            method='GET',
            url='/frontend-api/user/my-profile',
            token=token,
        )

        result = UserProfileResponse.model_validate(response) if response else None
        return result if result else None

    def stop_task_on_instance(
            self,
            token: str,
            task_id: int,
    ) -> Optional[TheStageBaseResponse]:
        data = {
            "taskId": task_id,
        }

        response = self._request(
            method='POST',
            url='/user-api/v1/task/cancel-task',
            data=data,
            token=token,
        )

        result = TheStageBaseResponse.model_validate(response) if response else None
        return result if result else None

    def get_container_list(
            self,
            token: str,
            query_string: Optional[str] = None,
            instance_rented_id: Optional[int] = None,
            selfhosted_instance_id: Optional[int] = None,
            sketch_id: Optional[int] = None,
            statuses: List[ContainerStatusEnumDto] = [],
            page: int = 1,
            limit: int = 10,
    ) -> Tuple[List[DockerContainerDto], int]:
        data = {
            "entityFilterRequest": {
                "orderByField": "id",
                "orderByDirection": "DESC",
                "page": page,
                "limit": limit
            },
            "instanceRentedId": instance_rented_id,
            "selfhostedInstanceId": selfhosted_instance_id,
            "sketchId": sketch_id,
            "queryString": query_string,
            "statuses": statuses
        }

        response = self._request(
            method='POST',
            url='/user-api/v1/docker-container/list',
            data=data,
            token=token,
        )

        result = DockerContainerListResponse.model_validate(response) if response else None
        return (result.paginated_list.entities, result.paginated_list.pagination_data.total_pages) if result and result.is_success and result.paginated_list else ([], None)

    def get_container_item(
            self,
            token: str,
            container_slug: Optional[str] = None,
            container_id: Optional[int] = None,
    ) -> Optional[DockerContainerItemResponse]:
        if not container_slug and not container_id:
            return None

        if container_id:
            data = {
                "dockerContainerId": container_id,
            }
        else:
            data = {
                "dockerContainerSlug": container_slug,
            }

        response = self._request(
            method='POST',
            url='/user-api/v1/docker-container/view',
            data=data,
            token=token,
        )

        return DockerContainerItemResponse.model_validate(response).docker_container if response else None

    def container_create(
            self,
            token: str,
            request_param: DockerContainerCreateRequestDto,
    ) -> bool:

        response = self._request(
            method='POST',
            url='/user-api/v1/docker-container/create',
            data=request_param.model_dump(by_alias=True),
            token=token,
        )

        result = TheStageBasePaginatedResponse.model_validate(response) if response else None
        return result.is_success if result and result.is_success else False

    def container_action(
            self,
            token: str,
            request_param: DockerContainerActionRequestDto,
    ) -> bool:

        response = self._request(
            method='POST',
            url='/user-api/v1/docker-container/action',
            data=request_param.model_dump(by_alias=True),
            token=token,
        )

        result = TheStageBasePaginatedResponse.model_validate(response) if response else None
        return result.is_success if result and result.is_success else False
