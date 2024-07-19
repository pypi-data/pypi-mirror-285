from typing import Tuple, List, Optional, Any

import typer
from thestage_core.entities.config_entity import ConfigEntity

from thestage.i18n.translation import __
from thestage.services.clients.thestage_api.dtos.enums.selfhosted_status import SelfHostedBusinessStatusEnumDto
from thestage.services.clients.thestage_api.dtos.enums.rented_status import RentedBusinessStatusEnumDto
from thestage.services.abstract_service import AbstractService
from thestage.helpers.error_handler import error_handler
from thestage.services.clients.thestage_api.api_client import TheStageApiClient
from thestage.services.clients.thestage_api.dtos.instance_rented_response import InstanceRentedDto
from thestage.services.clients.thestage_api.dtos.selfhosted_instance_response import SelfHostedInstanceDto
from thestage.services.config_provider.config_provider import ConfigProvider
from thestage.services.remote_server_service import RemoteServerService


class InstanceService(AbstractService):

    __thestage_api_client: TheStageApiClient = None

    def __init__(
            self,
            thestage_api_client: TheStageApiClient,
            config_provider: ConfigProvider,
            remote_server_service: RemoteServerService,
    ):
        super(InstanceService, self).__init__(
            config_provider=config_provider
        )
        self.__thestage_api_client = thestage_api_client
        self.__remote_server_service = remote_server_service

    def get_rented_item(
            self,
            config: ConfigEntity,
            instance_slug: str,
    ) -> Optional[InstanceRentedDto]:
        return self.__thestage_api_client.get_rented_item(
            token=config.main.auth_token,
            instance_slug=instance_slug,
        )

    def get_self_hosted_item(
            self,
            config: ConfigEntity,
            instance_slug: str,
    ) -> Optional[SelfHostedInstanceDto]:
        return self.__thestage_api_client.get_selfhosted_item(
            token=config.main.auth_token,
            instance_slug=instance_slug,
        )

    @error_handler()
    def check_instance_status_to_connect(
            self,
            instance: InstanceRentedDto,
    ) -> InstanceRentedDto:
        if instance:
            if instance.frontend_status.status_key in [
                RentedBusinessStatusEnumDto.IN_QUEUE.name,
                RentedBusinessStatusEnumDto.CREATING.name,
                RentedBusinessStatusEnumDto.REBOOTING.name,
                RentedBusinessStatusEnumDto.STARTING.name,
            ]:
                typer.echo(__('Instance start renting or rebooting, please connect late'))
                raise typer.Exit(1)
            elif instance.frontend_status.status_key in [
                RentedBusinessStatusEnumDto.TERMINATING.name,
                RentedBusinessStatusEnumDto.RENTAL_ERROR.name,
            ]:
                typer.echo(__('Instance is failed, please start him'))
                raise typer.Exit(1)
            elif instance.frontend_status.status_key in [
                RentedBusinessStatusEnumDto.STOPPED.name,
                RentedBusinessStatusEnumDto.STOPPING.name,
                RentedBusinessStatusEnumDto.DELETED.name,
            ]:
                typer.echo(__('Instance is stopped or deleted, please create new'))
                raise typer.Exit(1)
            elif instance.frontend_status.status_key in [
                RentedBusinessStatusEnumDto.UNKNOWN.name,
                RentedBusinessStatusEnumDto.ALL.name,
            ]:
                typer.echo(__('Instance status unknown'))
                raise typer.Exit(1)

        return instance

    @error_handler()
    def check_selfhosted_status_to_connect(
            self,
            instance: SelfHostedInstanceDto,
    ) -> SelfHostedInstanceDto:
        if instance:
            if instance.frontend_status.status_key in [
                SelfHostedBusinessStatusEnumDto.AWAITING_CONFIGURATION.name,
            ]:
                typer.echo(__('Instance awaiting to configuration'))
                raise typer.Exit(1)
            elif instance.frontend_status.status_key in [
                SelfHostedBusinessStatusEnumDto.TERMINATED.name,
                SelfHostedBusinessStatusEnumDto.DELETED.name,
            ]:
                typer.echo(__('Instance is failed or deleted, please start him'))
                raise typer.Exit(1)
            elif instance.frontend_status.status_key in [
                SelfHostedBusinessStatusEnumDto.UNKNOWN.name,
                SelfHostedBusinessStatusEnumDto.ALL.name,
            ]:
                typer.echo(__('Instance status unknown'))
                raise typer.Exit(1)

        return instance

    @error_handler()
    def connect_to_instance(
            self,
            ip_address: str,
            username: str,
    ):
        self.__remote_server_service.connect_to_instance(
            ip_address=ip_address,
            username=username,
        )

    @error_handler()
    def get_rented_list(
            self,
            config: ConfigEntity,
            statuses: List[RentedBusinessStatusEnumDto],
            row: int = 5,
            page: int = 1,
    ) -> Tuple[List[Any], int]:
        data, total_pages = self.__thestage_api_client.get_rented_instance_list(
            token=config.main.auth_token,
            statuses=statuses,
            page=page,
            limit=row,
        )

        return data, total_pages

    @error_handler()
    def get_self_hosted_list(
            self,
            config: ConfigEntity,
            statuses: List[SelfHostedBusinessStatusEnumDto],
            row: int = 5,
            page: int = 1,
    ) -> Tuple[List[Any], int]:
        data, total_pages = self.__thestage_api_client.get_selfhosted_instance_list(
            token=config.main.auth_token,
            statuses=statuses,
            page=page,
            limit=row,
        )
        return data, total_pages
