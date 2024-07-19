from datetime import datetime
from typing import Optional, List

from pydantic import Field, BaseModel, ConfigDict

from thestage.services.clients.thestage_api.dtos.base_response import TheStageBasePaginatedResponse
from thestage.services.clients.thestage_api.dtos.frontend_status import FrontendStatusDto
from thestage.services.clients.thestage_api.dtos.pagination_data import PaginationData
from thestage.services.clients.thestage_api.dtos.instance_detected_gpus import InstanceDetectedGpusDto
from thestage.services.clients.thestage_api.dtos.enums.instance_type import InstanceTypeEnumDto
from thestage.services.clients.thestage_api.dtos.enums.selfhosted_status import SelfHostedStatusEnumDto, \
    SelfHostedBusinessStatusEnumDto
from thestage.services.clients.thestage_api.dtos.enums.cpu_type import CpuTypeEnumDto


class SelfHostedInstanceDto(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    instance_type: Optional[InstanceTypeEnumDto] = Field(InstanceTypeEnumDto.UNKNOWN, alias='instanceType')
    id: Optional[int] = Field(None, alias='id')
    ram_size_gb: Optional[int] = Field(None, alias='ramSizeGb')
    client_id: Optional[int] = Field(None, alias='clientId')
    slug: Optional[str] = Field(None, alias='slug')
    title: Optional[str] = Field(None, alias='title')
    cpu_type: Optional[CpuTypeEnumDto] = Field(CpuTypeEnumDto.UNKNOWN, alias='cpuType')
    cpu_name: Optional[str] = Field(None, alias='cpuName')
    cpu_cores: Optional[int] = Field(None, alias='cpuCores')
    gpu_count: Optional[int] = Field(None, alias='gpuCount')
    detected_gpus: Optional[InstanceDetectedGpusDto] = Field(None, alias='detectedGpus')
    hardware_profile_id: Optional[str] = Field(None, alias='hardwareProfileId')
    disk_size_gb: Optional[int] = Field(None, alias='diskSizeGb')

    frontend_status: Optional[FrontendStatusDto] = Field(None, alias='frontendStatus')
    business_status: SelfHostedBusinessStatusEnumDto = Field(SelfHostedBusinessStatusEnumDto.UNKNOWN, alias='businessStatus')

    updated_at: Optional[datetime] = Field(None, alias='updatedAt')
    created_at: Optional[datetime] = Field(None, alias='createdAt')
    ip_address: Optional[str] = Field(None, alias='ipAddress')
    # not present now
    host_username: Optional[str] = Field(None, alias='hostUsername')


class SelfHostedInstanceListPaginated(TheStageBasePaginatedResponse):
    model_config = ConfigDict(use_enum_values=True)

    entities: List[SelfHostedInstanceDto] = Field(default_factory=list, alias='entities')
    pagination_data: Optional[PaginationData] = Field(None, alias='paginationData')


class SelfHostedInstanceListResponse(TheStageBasePaginatedResponse):
    paginated_list: Optional[SelfHostedInstanceListPaginated] = Field(None, alias='selfHostedInstanceList')


class SelfHostedRentedItemResponse(TheStageBasePaginatedResponse):
    model_config = ConfigDict(use_enum_values=True)

    selfhosted_instance: Optional[SelfHostedInstanceDto] = Field(None, alias='selfhostedInstance')
