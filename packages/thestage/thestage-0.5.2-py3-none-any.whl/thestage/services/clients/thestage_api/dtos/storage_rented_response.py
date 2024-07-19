from datetime import datetime
from typing import Optional, List

from pydantic import Field, BaseModel, ConfigDict

from thestage.services.clients.thestage_api.dtos.base_response import TheStageBaseResponse
from thestage.services.clients.thestage_api.dtos.pagination_data import PaginationData
from thestage.services.clients.thestage_api.dtos.enums.access_type import AccessTypeEnumDto
from thestage.services.clients.thestage_api.dtos.enums.drive_type import DriveTypeEnumDto
from thestage.services.clients.thestage_api.dtos.cloud_provider_region import CloudProviderRegionDto
from thestage.services.clients.thestage_api.dtos.enums.rented_status import RentedStatusEnumDto
from thestage.services.clients.thestage_api.dtos.enums.storage_type import StorageTypeEnumDto


class StorageRentedDto(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    id: Optional[int] = Field(None, alias='id')
    #prices_per_hour: Optional[List[PriceDefinitionDto]] = Field(default_factory=list, alias='pricesPerHour')
    #total_stagi_spent: Optional[PriceDefinitionDto] = Field(None, alias='totalStagiSpent')
    fk_client: Optional[int] = Field(None, alias='fkClient')
    slug: Optional[str] = Field(None, alias='slug')
    title: Optional[str] = Field(None, alias='title')
    fk_cloud_provider_region: Optional[int] = Field(None, alias='fkCloudProviderRegion')
    cloud_provider_region: Optional[CloudProviderRegionDto] = Field(None, alias='cloudProviderRegion')
    storage_type: StorageTypeEnumDto = Field(StorageTypeEnumDto.UNKNOWN, alias='storageType')
    drive_type: DriveTypeEnumDto = Field(DriveTypeEnumDto.UNKNOWN, alias='driveType')
    access_type: AccessTypeEnumDto = Field(AccessTypeEnumDto.UNKNOWN, alias='accessType')
    storage_size_gb: Optional[int] = Field(None, alias='storageSizeGb')
    provider_id: Optional[str] = Field(None, alias='providerId')
    is_active: Optional[bool] = Field(False, alias='isActive')
    status: RentedStatusEnumDto = Field(RentedStatusEnumDto.UNKNOWN, alias='status')
    created_at: Optional[datetime] = Field(None, alias='createdAt')
    updated_at: Optional[datetime] = Field(None, alias='updatedAt')
    aws_access_key: Optional[str] = Field(None, alias='awsAccessKey')
    aws_secret_key: Optional[str] = Field(None, alias='awsSecretKey')
    endpoint: Optional[str] = Field(None, alias='endpoint')


class StorageRentedListResponse(TheStageBaseResponse):
    entities: List[StorageRentedDto] = Field(default_factory=list, alias='entities')
    current_page: Optional[int] = Field(None, alias='currentPage')
    last_page: Optional[bool] = Field(None, alias='lastPage')
    total_pages: Optional[int] = Field(None, alias='totalPages')
    pagination_data: Optional[PaginationData] = Field(None, alias='paginationData')
