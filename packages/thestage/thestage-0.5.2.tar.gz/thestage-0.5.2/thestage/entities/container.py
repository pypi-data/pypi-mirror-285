from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DockerContainerEntity(BaseModel):

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    id: Optional[int] = Field(None, alias='id')
    status: Optional[str] = Field(None, alias='STATUS')
    slug: Optional[str] = Field(None, alias='UNIQUE ID')
    title: Optional[str] = Field(None, alias='TITLE')
    instance_rented_slug: Optional[str] = Field(None, alias='INSTANCE UNIQUE ID')
    selfhosted_rented_slug: Optional[str] = Field(None, alias='SELF-HOSTED UNIQUE ID')
    system_name: Optional[str] = Field(None, alias='SYSTEM NAME')
    docker_image: Optional[str] = Field(None, alias='DOCKER IMAGE')
