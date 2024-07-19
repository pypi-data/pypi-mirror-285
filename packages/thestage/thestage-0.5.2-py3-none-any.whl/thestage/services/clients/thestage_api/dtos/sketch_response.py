from typing import Optional

from pydantic import Field, BaseModel, ConfigDict

from thestage.services.clients.thestage_api.dtos.selfhosted_instance_response import SelfHostedInstanceDto
from thestage.services.clients.thestage_api.dtos.task_response import TaskDto
from thestage.services.clients.thestage_api.dtos.instance_rented_response import InstanceRentedDto
from thestage.services.clients.thestage_api.dtos.storage_rented_response import StorageRentedDto
from thestage.services.clients.thestage_api.dtos.base_response import TheStageBaseResponse


class SketchDto(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    id: Optional[int] = Field(None, alias='id')
    client_id: Optional[int] = Field(None, alias='fkClient')
    fk_instance_rented_default: Optional[int] = Field(None, alias='fkInstanceRentedDefault')
    fk_selfhosted_instance_default: Optional[int] = Field(None, alias='fkSelfhostedInstanceDefault')
    fk_storage_rented_default: Optional[int] = Field(None, alias='fkStorageRentedDefault')
    ssh_key_deploy: Optional[int] = Field(None, alias='fkSshKeyDeploy')
    name: Optional[str] = Field(None, alias='name')
    slug: Optional[str] = Field(None, alias='slug')
    description: Optional[str] = Field(None, alias='description')
    github_username: Optional[str] = Field(None, alias='githubCollaboratorUsername')

    last_commit_hash: Optional[str] = Field(None, alias='lastCommitHash')
    last_commit_description: Optional[str] = Field(None, alias='lastCommitDescription')
    git_repository_url: Optional[str] = Field(None, alias='gitRepositoryUrl')
    git_repository_name: Optional[str] = Field(None, alias='gitRepositoryName')

    task_count: Optional[int] = Field(None, alias='taskCount')
    favourite_task_count: Optional[int] = Field(None, alias='favouriteTaskCount')

    last_task_run_date: Optional[str] = Field(None, alias='lastTaskRunDate')
    created_at: Optional[str] = Field(None, alias='createdAt')
    updated_at: Optional[str] = Field(None, alias='updatedAt')
    instance_rented_default: Optional[InstanceRentedDto] = Field(None, alias='instanceRentedDefault')
    selfhosted_instance_default: Optional[SelfHostedInstanceDto] = Field(None, alias='selfhostedInstanceDefault')
    storage_rented_default: Optional[StorageRentedDto] = Field(None, alias='storageRentedDefault')


class SketchViewResponse(TheStageBaseResponse):
    sketch: Optional[SketchDto] = Field(None, alias='sketch')


class SketchRunTaskResponse(TheStageBaseResponse):
    task: Optional[TaskDto] = Field(None, alias='task')
