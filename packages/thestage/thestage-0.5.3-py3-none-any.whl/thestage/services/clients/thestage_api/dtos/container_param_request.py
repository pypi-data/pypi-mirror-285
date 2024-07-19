from typing import Optional, List

from pydantic import Field, BaseModel, ConfigDict

from thestage.services.clients.thestage_api.dtos.enums.container_pending_action import ContainerPendingActionEnumDto
from thestage.services.clients.thestage_api.dtos.docker_container_mapping import DockerContainerMappingDto


class DockerContainerCreateRequestDto(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    fk_instance_rented: Optional[int] = Field(None, alias='fkInstanceRented')
    fk_selfhosted_instance: Optional[int] = Field(None, alias='fkSelfhostedInstance')
    fk_sketch: Optional[int] = Field(None, alias='fkSketch')

    title: Optional[str] = Field(None, alias='title')
    slug: Optional[str] = Field(None, alias='slug')
    docker_image: Optional[str] = Field(None, alias='dockerImage')
    assigned_cpus: Optional[int] = Field(None, alias='assignedCpus')
    assigned_gpu_ids: List[int] = Field(default_factory=list, alias='assignedGpuIds')
    mappings: Optional[DockerContainerMappingDto] = Field(None, alias='mappings')
    container_count: Optional[int] = Field(None, alias='containerCount')


class DockerContainerActionRequestDto(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    container_id: Optional[int] = Field(None, alias='dockerContainerId')
    action: ContainerPendingActionEnumDto = Field(ContainerPendingActionEnumDto.UNKNOWN, alias='action')
