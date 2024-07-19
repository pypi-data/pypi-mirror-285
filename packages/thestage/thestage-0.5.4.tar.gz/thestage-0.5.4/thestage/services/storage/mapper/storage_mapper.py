from abc import ABC
from typing import Optional, Any

from thestage.services.abstract_mapper import AbstractMapper
from thestage.entities.storage import StorageEntity
from thestage.services.clients.thestage_api.dtos.storage_rented_response import StorageRentedDto


class StorageMapper(AbstractMapper):

    @staticmethod
    def build_entity(item: StorageRentedDto) -> Optional[StorageEntity]:
        if not item:
            return None

        return StorageEntity(
            slug=item.slug,
            title=item.title,
            provider_id=item.provider_id,
            status=item.status,
            is_active=item.is_active,
            created_at=item.created_at.strftime("%Y-%m-%d %H:%M:%S") if item.created_at else '',
            updated_at=item.updated_at.strftime("%Y-%m-%d %H:%M:%S") if item.updated_at else '',
        )
