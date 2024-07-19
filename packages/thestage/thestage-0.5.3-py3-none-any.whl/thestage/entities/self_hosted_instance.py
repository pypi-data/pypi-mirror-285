from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class SelfHostedInstanceEntity(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    id: Optional[int] = Field(None, alias='id')
    slug: Optional[str] = Field(None, alias='slug')
    title: Optional[str] = Field(None, alias='title')
    cpu_type: Optional[str] = Field(str, alias='cpu_type')
    cpu_cores: Optional[int] = Field(None, alias='cpu_cores')
    ram_size_gb: Optional[int] = Field(None, alias='ram_size_gb')
    ip_address: Optional[str] = Field(None, alias='ip_address')
    username: Optional[str] = Field(None, alias='username')
    status: Optional[str] = Field(None, alias='status')
    created_at: Optional[str] = Field(None, alias='created_at')
    updated_at: Optional[str] = Field(None, alias='updated_at')
