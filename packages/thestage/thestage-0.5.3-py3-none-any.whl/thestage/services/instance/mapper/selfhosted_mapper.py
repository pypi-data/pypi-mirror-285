from abc import ABC
from typing import Optional, Any, Tuple

from thestage.entities.rented_instance import RentedInstanceEntity
from thestage.services.clients.thestage_api.dtos.selfhosted_instance_response import SelfHostedInstanceDto
from thestage.services.abstract_mapper import AbstractMapper


class SelfHostedMapper(AbstractMapper):

    @staticmethod
    def get_exclude_fields() -> Tuple:
        return 'id', 'username', 'ram_size_gb'

    @staticmethod
    def build_entity(item: SelfHostedInstanceDto) -> Optional[RentedInstanceEntity]:
        if not item:
            return None

        gpus = []
        if item.detected_gpus:
            gpus = [item.type.value for item in item.detected_gpus.gpus]

        if len(gpus) == 0:
            gpus = ['NO_GPU']

        return RentedInstanceEntity(
            id=item.id,
            slug=item.slug,
            title=item.title,
            cpu_type=item.cpu_type,
            cpu_cores=item.cpu_cores,
            gpu_type=', '.join(gpus),
            ram_size_gb=item.ram_size_gb,
            ip_address=item.ip_address,
            username=item.host_username,
            status=item.frontend_status.status_translation if item.frontend_status else None,
            created_at=item.created_at.strftime("%Y-%m-%d %H:%M:%S") if item.created_at else '',
            updated_at=item.updated_at.strftime("%Y-%m-%d %H:%M:%S") if item.updated_at else '',
        )
