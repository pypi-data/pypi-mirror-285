from typing import Optional, Tuple

from thestage.services.clients.thestage_api.dtos.container_response import DockerContainerDto
from thestage.entities.container import DockerContainerEntity
from thestage.services.abstract_mapper import AbstractMapper


class ContainerMapper(AbstractMapper):

    @staticmethod
    def get_exclude_fields() -> Tuple:
        return ('id', 'system_name')

    @staticmethod
    def build_entity(item: DockerContainerDto) -> Optional[DockerContainerEntity]:
        if not item:
            return None

        return DockerContainerEntity(
            id=item.id,
            status=item.status_to_display,
            slug=item.slug,
            title=item.title,
            instance_rented_slug=item.instance_rented.slug if item.instance_rented else '',
            selfhosted_rented_slug=item.selfhosted_instance.slug if item.selfhosted_instance else '',
            system_name=item.system_name,
            docker_image=item.docker_image,
        )
