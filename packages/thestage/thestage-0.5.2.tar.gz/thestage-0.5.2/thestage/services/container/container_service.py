import os
from typing import List, Tuple, Optional

import typer
from thestage_core.entities.config_entity import ConfigEntity
from thestage_core.services.filesystem_service import FileSystemServiceCore

from thestage.helpers.logger.app_logger import app_logger
from thestage.services.clients.thestage_api.dtos.container_param_request import DockerContainerActionRequestDto
from thestage.services.clients.thestage_api.dtos.enums.container_pending_action import ContainerPendingActionEnumDto
from thestage.services.clients.thestage_api.dtos.enums.container_status import ContainerStatusEnumDto
from thestage.entities.enums.shell_type import ShellType
from thestage.services.clients.thestage_api.dtos.sftp_path_helper import SftpPathHelper
from thestage.services.remote_server_service import RemoteServerService
from thestage.i18n.translation import __
from thestage.services.abstract_service import AbstractService
from thestage.services.clients.thestage_api.dtos.container_response import DockerContainerDto
from thestage.helpers.error_handler import error_handler
from thestage.services.clients.thestage_api.api_client import TheStageApiClient
from thestage.services.config_provider.config_provider import ConfigProvider


class ContainerService(AbstractService):

    __thestage_api_client: TheStageApiClient = None

    def __init__(
            self,
            thestage_api_client: TheStageApiClient,
            config_provider: ConfigProvider,
            remote_server_service: RemoteServerService,
            file_system_service: FileSystemServiceCore,
    ):
        super(ContainerService, self).__init__(
            config_provider=config_provider
        )
        self.__thestage_api_client = thestage_api_client
        self.__remote_server_service = remote_server_service
        self.__file_system_service = file_system_service

    @error_handler()
    def get_list(
            self,
            config: ConfigEntity,
            statuses: List[ContainerStatusEnumDto],
            row: int = 5,
            page: int = 1,
    ) -> Tuple[List[DockerContainerDto], int]:

        data, total = self.__thestage_api_client.get_container_list(
            token=config.main.auth_token,
            statuses=statuses,
            page=page,
            limit=row,
        )

        return data, total

    @error_handler()
    def get_item(
            self,
            config: ConfigEntity,
            container_id: Optional[int] = None,
            container_slug: Optional[str] = None,
    ) -> Optional[DockerContainerDto]:
        return self.__thestage_api_client.get_container_item(
            token=config.main.auth_token,
            container_id=container_id,
            container_slug=container_slug,
        )

    @staticmethod
    def get_server_auth(
            container: DockerContainerDto,
            no_dialog: bool = False,
            username_param: Optional[str] = None,
    ) -> Tuple[str, str]:
        if container.instance_rented:
            username = container.instance_rented.host_username
            ip_address = container.instance_rented.ip_address
        elif container.selfhosted_instance:
            username = container.selfhosted_instance.host_username or 'root'
            ip_address = container.selfhosted_instance.ip_address
        else:
            typer.echo(__("Not found rented or selfhosted instance for connect"))
            raise typer.Exit(1)

        if not username_param:
            if not username:
                if no_dialog:
                    typer.echo(__('Please set up username as parameter on no-dialog mode'))
                    raise typer.Exit(1)

                username = typer.prompt(
                    default='ubuntu',
                    text=__('Please set up username to connect instance'),
                    show_choices=False,
                    type=str,
                    show_default=True,
                )
        else:
            username = username_param

        return username, ip_address

    @error_handler()
    def connect_container(
            self,
            config: ConfigEntity,
            container: DockerContainerDto,
            no_dialog: bool = False,
            username_param: Optional[str] = None,
    ):

        username, ip_address = self.get_server_auth(
            container=container,
            username_param=username_param,
            no_dialog=no_dialog,
        )

        if not container.system_name:
            typer.echo(__("Container name not present, can not connect to container"))
            raise typer.Exit(1)

        shell: Optional[ShellType] = self.__remote_server_service.get_shell_from_container(
            ip_address=ip_address,
            username=username,
            docker_name=container.system_name,
        )

        if not shell:
            typer.echo(__("We can not get shell on container (bash, shell), please use standard shell"))
            raise typer.Exit(1)

        self.__remote_server_service.connect_to_container(
            ip_address=ip_address,
            username=username,
            docker_name=container.system_name,
            shell=shell,
        )

    @error_handler()
    def check_container_status_for_start(
            self,
            container: DockerContainerDto,
    ) -> DockerContainerDto:
        if container:
            if container.status == ContainerStatusEnumDto.RUNNING:
                typer.echo(__('Container is running, can not start working server'))
                raise typer.Exit(1)
            elif container.status == ContainerStatusEnumDto.CREATING:
                typer.echo(__('Container creating, please check status later'))
                raise typer.Exit(1)
            elif container.status in [
                ContainerStatusEnumDto.STARTING,
                ContainerStatusEnumDto.RESTARTING,
            ]:
                typer.echo(__('The container starts now, you can be up and running in minutes'))
                raise typer.Exit(1)
            elif container.status in [
                ContainerStatusEnumDto.DELETING,
                ContainerStatusEnumDto.DELETED,
            ]:
                typer.echo(__('The container was deleted, create new'))
                raise typer.Exit(1)

        return container

    @error_handler()
    def check_container_status_for_stop(
            self,
            container: DockerContainerDto,
    ) -> DockerContainerDto:
        if container:
            if container.status in [
                ContainerStatusEnumDto.CREATING,
                ContainerStatusEnumDto.STARTING,
                ContainerStatusEnumDto.RESTARTING,
            ]:
                typer.echo(__('Container in rebooting or creating, please stop later'))
                raise typer.Exit(1)
            elif container.status in [
                ContainerStatusEnumDto.FAILED,
                ContainerStatusEnumDto.DEAD,
                ContainerStatusEnumDto.CREATING_FAILED,
                ContainerStatusEnumDto.STOPPING,
                ContainerStatusEnumDto.STOPPED,
            ]:
                typer.echo(__('Container was stopped, by error or manually'))
                raise typer.Exit(1)
            elif container.status in [
                ContainerStatusEnumDto.DELETING,
                ContainerStatusEnumDto.DELETED,
            ]:
                typer.echo(__('The container was deleted, create new'))
                raise typer.Exit(1)

        return container

    @error_handler()
    def check_container_status_for_work(
            self,
            container: DockerContainerDto,
    ) -> DockerContainerDto:
        if container:
            if container.status in [
                ContainerStatusEnumDto.CREATING,
                ContainerStatusEnumDto.STARTING,
                ContainerStatusEnumDto.RESTARTING,
            ]:
                typer.echo(__('Container is rebooted, please connect late'))
                raise typer.Exit(1)
            elif container.status in [
                ContainerStatusEnumDto.FAILED,
                ContainerStatusEnumDto.DEAD,
                ContainerStatusEnumDto.CREATING_FAILED,
                ContainerStatusEnumDto.STOPPING,
                ContainerStatusEnumDto.STOPPED,
            ]:
                typer.echo(__('Container is failed, please start him'))
                raise typer.Exit(1)
            elif container.status in [
                ContainerStatusEnumDto.DELETING,
                ContainerStatusEnumDto.DELETED,
            ]:
                typer.echo(__('Container was deleted, create new'))
                raise typer.Exit(1)

        return container

    @error_handler()
    def put_file_to_container(
            self,
            container: DockerContainerDto,
            src_path: str,
            destination_path: Optional[str] = None,
            is_folder: bool = False,
            no_dialog: bool = False,
            username_param: Optional[str] = None,
    ):

        username, ip_address = self.get_server_auth(
            container=container,
            username_param=username_param,
            no_dialog=no_dialog,
        )

        if not self.__file_system_service.check_if_path_exist(file=src_path):
            typer.echo(__("Not found path with file"))
            raise typer.Exit(1)

        if (not is_folder) and self.__file_system_service.is_folder(folder=src_path, auto_create=False, with_exception=False):
            typer.echo(__("Path is folder, please set up recursive flag"))
            raise typer.Exit(1)

        if container.mappings and container.mappings.directory_mappings:
            path_helper: SftpPathHelper = self.__remote_server_service.check_path_mapping(
                directory_mapping=container.mappings.directory_mappings,
                path=destination_path,
                is_upload=True,
                is_folder=is_folder,
            )
        else:
            typer.echo(__("Error, can not find mapping folders"))
            raise typer.Exit(1)

        if not path_helper.tmp_instance_path:
            typer.echo(__("Error, can not find mapping for /public folder"))
            raise typer.Exit(1)

        self.__remote_server_service.upload_data_to_container(
            ip_address=ip_address,
            username=username,
            docker_name=container.system_name,
            src_path=src_path,
            dest_path=destination_path,
            path_helper=path_helper,
            #real_path=real_path,
            #client_path=destination_path,
            #temporary_folder_path=temporary_folder_path,
            is_folder=is_folder,
        )

    @error_handler()
    def get_file_from_container(
            self,
            container: DockerContainerDto,
            src_path: str,
            destination_path: Optional[str] = None,
            is_folder: bool = False,
            no_dialog: bool = False,
            username_param: Optional[str] = None,
    ):
        username, ip_address = self.get_server_auth(
            container=container,
            username_param=username_param,
            no_dialog=no_dialog,
        )

        #if not self.__file_system_service.check_if_path_exist(file=destination_path):
        #    typer.echo(__("Not found path with file"))
        #    raise typer.Exit(1)

        if container.mappings and container.mappings.directory_mappings:
            path_helper: SftpPathHelper = self.__remote_server_service.check_path_mapping(
                directory_mapping=container.mappings.directory_mappings,
                path=src_path,
                is_upload=False,
                is_folder=is_folder,
            )
        else:
            typer.echo(__("Error, can not find mapping folders"))
            raise typer.Exit(1)

        if not path_helper.tmp_container_path:
            typer.echo(__("Error, can not find path to copy"))
            raise typer.Exit(1)

        self.__remote_server_service.download_data_to_container(
            ip_address=ip_address,
            username=username,
            docker_name=container.system_name,
            src_path=src_path,
            dest_path=destination_path,
            path_helper=path_helper,
            is_folder=is_folder,
        )

    @error_handler()
    def change_container_status(
            self,
            config: ConfigEntity,
            container: DockerContainerDto,
            action: ContainerPendingActionEnumDto,
    ) -> bool:
        request_params = DockerContainerActionRequestDto(
            dockerContainerId=container.id,
            action=action,
        )
        result = self.__thestage_api_client.container_action(
            token=config.main.auth_token,
            request_param=request_params,
        )
        if not result:
            app_logger.error(f'Container dont change status - {result}')

        return result
