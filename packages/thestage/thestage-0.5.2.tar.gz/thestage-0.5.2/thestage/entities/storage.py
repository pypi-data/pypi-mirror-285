from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class StorageEntity(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    slug: Optional[str] = Field(None, alias='slug')
    title: Optional[str] = Field(None, alias='title')
    provider_id: Optional[str] = Field(None, alias='provider_id')
    status: Optional[str] = Field(None, alias='status')
    is_active: Optional[bool] = Field(False, alias='is_active')
    created_at: Optional[str] = Field(None, alias='created_at')
    updated_at: Optional[str] = Field(None, alias='updated_at')
