from typing import Optional, List

from pydantic import Field, BaseModel, ConfigDict

from thestage.services.clients.thestage_api.dtos.docker_container_assigned_device import DockerContainerAssignedDeviceDto
from thestage.services.clients.thestage_api.dtos.docker_container_mapping import DockerContainerMappingDto
from thestage.services.clients.thestage_api.dtos.enums.container_pending_action import ContainerPendingActionEnumDto
from thestage.services.clients.thestage_api.dtos.enums.container_status import ContainerStatusEnumDto
from thestage.services.clients.thestage_api.dtos.installed_service import DockerContainerInstalledServicesDto
from thestage.services.clients.thestage_api.dtos.instance_rented_response import InstanceRentedDto
from thestage.services.clients.thestage_api.dtos.project_response import ProjectDto
from thestage.services.clients.thestage_api.dtos.selfhosted_instance_response import SelfHostedInstanceDto
from thestage.services.clients.thestage_api.dtos.base_response import TheStageBaseResponse, TheStageBasePaginatedResponse
from thestage.services.clients.thestage_api.dtos.pagination_data import PaginationData


class DockerContainerDto(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    id: Optional[int] = Field(None, alias='id')
    instance_rented_id: Optional[int] = Field(None, alias='instanceRentedId')
    selfhosted_instance_id: Optional[int] = Field(None, alias='selfhostedInstanceId')
    instance_rented: Optional[InstanceRentedDto] = Field(None, alias='instanceRented')
    selfhosted_instance: Optional[SelfHostedInstanceDto] = Field(None, alias='selfhostedInstance')

    project_id: Optional[int] = Field(None, alias='projectId')
    porject: Optional[ProjectDto] = Field(None, alias='project')

    is_default: Optional[bool] = Field(None, alias='isDefault')
    system_name: Optional[str] = Field(None, alias='systemName')
    title: Optional[str] = Field(None, alias='title')
    slug: Optional[str] = Field(None, alias='slug')
    docker_image: Optional[str] = Field(None, alias='dockerImage')
    assigned_devices: Optional[DockerContainerAssignedDeviceDto] = Field(None, alias='assignedDevices')
    mappings: Optional[DockerContainerMappingDto] = Field(None, alias='mappings')
    status: ContainerStatusEnumDto = Field(ContainerStatusEnumDto.UNKNOWN, alias='status')
    status_to_display: Optional[str] = Field(None, alias='statusToDisplay')
    pending_action: Optional[ContainerPendingActionEnumDto] = Field(None, alias='pendingAction')
    installed_services: Optional[DockerContainerInstalledServicesDto] = Field(None, alias='installedServices')
    created_at: Optional[str] = Field(None, alias='createdAt')
    updated_at: Optional[str] = Field(None, alias='updatedAt')


class DockerContainerPaginated(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    entities: List[DockerContainerDto] = Field(default_factory=list, alias='entities')
    current_page: Optional[int] = Field(None, alias='currentPage')
    last_page: Optional[bool] = Field(None, alias='lastPage')
    total_pages: Optional[int] = Field(None, alias='totalPages')
    pagination_data: Optional[PaginationData] = Field(None, alias='paginationData')


class DockerContainerListResponse(TheStageBasePaginatedResponse):
    paginated_list: Optional[DockerContainerPaginated] = Field(None, alias='paginatedList')


class DockerContainerItemResponse(TheStageBasePaginatedResponse):
    docker_container: Optional[DockerContainerDto] = Field(None, alias='dockerContainer')
