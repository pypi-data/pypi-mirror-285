import pathlib
from typing import Optional, List

from thestage.services.clients.thestage_api.dtos.enums.container_status import ContainerStatusEnumDto
from thestage.services.clients.thestage_api.dtos.enums.container_pending_action import ContainerPendingActionEnumDto
from thestage.services.clients.thestage_api.dtos.container_response import DockerContainerDto
from thestage.i18n.translation import __
from thestage.services.container.container_service import ContainerService
from thestage.services.container.mapper.container_mapper import ContainerMapper
from thestage.helpers.logger.app_logger import app_logger
from thestage.controllers.utils_controller import base_check_validation, get_current_directory, base_global_check_validation

import typer


app = typer.Typer(no_args_is_help=True, help=__("Help working with containers"))


@app.command(name='ls', help=__("Show list containers"))
def list_items(
        row: int = typer.Option(
            5,
            '--row',
            '-r',
            help=__("Count row in table"),
            is_eager=False,
        ),
        page: int = typer.Option(
            1,
            '--page',
            '-p',
            help=__("Page number"),
            is_eager=False,
        ),
        statuses: List[ContainerStatusEnumDto] = typer.Option(
            ["RUNNING", "BUSY"],
            '--status',
            '-s',
            help=__("Status item (ALL - show all containers)"),
            is_eager=False,
        ),
        no_dialog: Optional[bool] = typer.Option(
            None,
            "--no-dialog",
            "-nd",
            help=__("Start process with default values, without future dialog"),
            is_eager=False,
        ),
):
    """
        List containers
    """
    path = get_current_directory()
    app_logger.info(f'Start container lists from {path}')

    config, facade = base_global_check_validation(path=path, no_dialog=no_dialog)

    headers = [
        'STATUS',
        'UNIQUE ID',
        'TITLE',
        'INSTANCE UNIQUE ID',
        'SELF-HOSTED UNIQUE ID',
        'DOCKER IMAGE',
    ]

    container_service: ContainerService = facade.get_container_service()

    typer.echo(__(
        "Start show container list with statuses: %statuses% (You can show all statuses set up status=ALL)",
        placeholders={
            'statuses': ', '.join([item.value for item in statuses])
        }))

    if ContainerStatusEnumDto.find_special_status(statuses=statuses):
        statuses = []

    container_service.print(
        func_get_data=container_service.get_list,
        func_special_params={
            'statuses': statuses,
        },
        mapper=ContainerMapper(),
        config=config,
        headers=headers,
        row=row,
        page=page,
        no_dialog=no_dialog,
        max_col_width=[10, 20, 30, 30, 30, 20, 20, 20],
        show_index="never",
    )

    typer.echo(__("List containers done"))
    raise typer.Exit(0)


@app.command(name="info", help=__("Show details container"))
def item_details(
        container_slug: Optional[str] = typer.Option(
            None,
            '--container-uniqueid',
            '-s',
            help=__("Container unique id"),
            is_eager=False,
        ),
        no_dialog: Optional[bool] = typer.Option(
            None,
            "--no-dialog",
            "-nd",
            help=__("Start process with default values, without future dialog"),
            is_eager=False,
        ),
):
    """
        Show container details
    """
    path = get_current_directory()
    app_logger.info(f'Start container details')

    if not container_slug:
        typer.echo(__('Container id or container slug is required'))
        raise typer.Exit(1)

    config, facade = base_check_validation(path=path, no_dialog=no_dialog)

    container_service: ContainerService = facade.get_container_service()

    container: Optional[DockerContainerDto] = container_service.get_item(
        config=config,
        container_slug=container_slug,
    )

    if not container:
        typer.echo(__("Not found container - %container_item%", {'container_item': str(container_slug) if container_slug else ''}))
        raise typer.Exit(1)

    typer.echo(__('CONTAINER DATA:'))
    typer.echo(__("STATUS: %status%", {'status': str(container.status_to_display)}))
    typer.echo(__("UNIQUE ID: %slug%", {'slug': str(container.slug)}))
    typer.echo(__("TITLE: %title%", {'title': str(container.title)}))

    if container.instance_rented:
        typer.echo(
            __("INSTANCE RANTED UNIQUE ID: %instance_slug%", {'instance_slug': str(container.instance_rented.slug)})
        )
        typer.echo(
            __("INSTANCE STATUS: %instance_status%",
               {'instance_status': str(container.instance_rented.frontend_status.status_translation if container.instance_rented.frontend_status else 'UNKNOWN')})
        )

    if container.selfhosted_instance:
        typer.echo(
            __("SELFHOSTED INSTANCE UNIQUE ID: %instance_slug%", {'instance_slug': str(container.selfhosted_instance.slug)})
        )
        typer.echo(
            __("SELFHOSTED INSTANCE STATUS: %instance_status%",
               {'instance_status': str(container.selfhosted_instance.frontend_status.status_translation if container.selfhosted_instance.frontend_status else 'UNKNOWN')})
        )

    if container.mappings and (container.mappings.port_mappings or container.mappings.directory_mappings):
        if container.mappings.port_mappings:
            typer.echo(__("CONTAINER PORT MAPPING:"))
            for src, dest in container.mappings.port_mappings.items():
                typer.echo(f"    {src} : {dest}")

        if container.mappings.directory_mappings:
            typer.echo(__("CONTAINER DIRECTORY MAPPING:"))
            for src, dest in container.mappings.directory_mappings.items():
                typer.echo(f"    {src} : {dest}")

    typer.echo(__("Container details done"))
    raise typer.Exit(0)


@app.command(name="connect", help=__("Help connect to container"))
def container_connect(
        container_slug: Optional[str] = typer.Option(
            None,
            '--container-uniqueid',
            '-s',
            help=__("Container unique id"),
            is_eager=False,
        ),
        username: Optional[str] = typer.Option(
            None,
            '--username',
            '-u',
            help=__("Instance username if use selfhosted"),
            is_eager=False,
        ),
        no_dialog: Optional[bool] = typer.Option(
            None,
            "--no-dialog",
            "-nd",
            help=__("Start process with default values, without future dialog"),
            is_eager=False,
        ),
):
    """
        Show container details
    """
    path = get_current_directory()
    app_logger.info(f'Connect to container')

    if not container_slug:
        typer.echo(__('Container id or container slug is required'))
        raise typer.Exit(1)

    config, facade = base_global_check_validation(path=path, no_dialog=no_dialog)

    container_service: ContainerService = facade.get_container_service()

    container: Optional[DockerContainerDto] = container_service.get_item(
        config=config,
        container_slug=container_slug,
    )

    if container:
        container_service.check_container_status_for_work(
            container=container
        )
        container_service.connect_container(
            config=config,
            container=container,
            no_dialog=no_dialog,
            username_param=username,
        )
    else:
        typer.echo(__("Not found container - %container_item%", {'container_item': container_slug}))

    app_logger.info(f'Stop connect to container')
    raise typer.Exit(0)


@app.command(name="upload", help=__("Help copy file to container"))
def put_file(
        container_slug: Optional[str] = typer.Option(
            None,
            '--container-uniqueid',
            '-s',
            help=__("Container unique id"),
            is_eager=False,
        ),
        source_path: str = typer.Option(
            None,
            '--target-path',
            '-sp',
            help=__("Path to file for copy"),
            is_eager=True,
        ),
        destination_path: Optional[str] = typer.Option(
            None,
            '--destination-path',
            '-dp',
            help=__("Path destination copy"),
            is_eager=False,
        ),
        is_recursive: bool = typer.Option(
            False,
            "--is-recursive",
            "-r",
            help=__("Recursive flag help copy folders"),
            is_eager=False,
        ),
        username: Optional[str] = typer.Option(
            None,
            '--username',
            '-u',
            help=__("Instance username if use selfhosted"),
            is_eager=False,
        ),
        no_dialog: Optional[bool] = typer.Option(
            None,
            "--no-dialog",
            "-nd",
            help=__("Start process with default values, without future dialog"),
            is_eager=False,
        ),
):
    """
        Push file to container
    """
    path = get_current_directory()
    app_logger.info(f'Push file to container')

    if not container_slug:
        typer.echo(__('Container id or container slug is required'))
        raise typer.Exit(1)

    config, facade = base_global_check_validation(path=path, no_dialog=no_dialog)

    container_service: ContainerService = facade.get_container_service()

    container: Optional[DockerContainerDto] = container_service.get_item(
        config=config,
        container_slug=container_slug,
    )

    if container:
        container_service.check_container_status_for_work(
            container=container
        )

        container_service.put_file_to_container(
            container=container,
            src_path=source_path,
            destination_path=destination_path,
            is_folder=is_recursive,
            no_dialog=no_dialog,
            username_param=username,
        )
    else:
        typer.echo(__("Not found container - %container_item%", {'container_item': container_slug}))

    app_logger.info(f'End send files to container')
    raise typer.Exit(0)


@app.command(name="download", help=__("Help copy file from container"))
def download_file(
        container_slug: Optional[str] = typer.Option(
            None,
            '--container-uniqueid',
            '-s',
            help=__("Container unique id"),
            is_eager=False,
        ),
        source_path: str = typer.Option(
            None,
            '--target-path',
            '-sp',
            help=__("Path to file for copy"),
            is_eager=True,
        ),
        destination_path: Optional[str] = typer.Option(
            None,
            '--destination-path',
            '-dp',
            help=__("Path destination copy"),
            is_eager=False,
        ),
        is_recursive: bool = typer.Option(
            False,
            "--is-recursive",
            "-r",
            help=__("Recursive flag help copy folders"),
            is_eager=False,
        ),
        username: Optional[str] = typer.Option(
            None,
            '--username',
            '-u',
            help=__("Instance username if use selfhosted"),
            is_eager=False,
        ),
        no_dialog: Optional[bool] = typer.Option(
            None,
            "--no-dialog",
            "-nd",
            help=__("Start process with default values, without future dialog"),
            is_eager=False,
        ),
):
    """
        Download file from container
    """
    path = get_current_directory()
    app_logger.info(f'Download file from container')

    if not container_slug:
        typer.echo(__('Container id or container slug is required'))
        raise typer.Exit(1)

    config, facade = base_global_check_validation(path=path, no_dialog=no_dialog)

    container_service: ContainerService = facade.get_container_service()

    container: Optional[DockerContainerDto] = container_service.get_item(
        config=config,
        container_slug=container_slug,
    )

    if container:
        container_service.check_container_status_for_work(
            container=container
        )

        container_service.get_file_from_container(
            container=container,
            src_path=source_path,
            destination_path=destination_path,
            is_folder=is_recursive,
            no_dialog=no_dialog,
            username_param=username,
        )
    else:
        typer.echo(__("Not found container - %container_item%", {'container_item': container_slug}))

    app_logger.info(f'End download files from container')
    raise typer.Exit(0)


@app.command(name="start", help=__("Help start container"))
def item_start(
        container_slug: Optional[str] = typer.Option(
            None,
            '--container-uniqueid',
            '-s',
            help=__("Container unique id"),
            is_eager=False,
        ),
        no_dialog: Optional[bool] = typer.Option(
            None,
            "--no-dialog",
            "-nd",
            help=__("Start process with default values, without future dialog"),
            is_eager=False,
        ),
):
    """
        Start container
    """
    path = get_current_directory()
    app_logger.info(f'Start container')

    if not container_slug:
        typer.echo(__('Container id or container slug is required'))
        raise typer.Exit(1)

    config, facade = base_global_check_validation(path=path, no_dialog=no_dialog)

    container_service: ContainerService = facade.get_container_service()

    container: Optional[DockerContainerDto] = container_service.get_item(
        config=config,
        container_slug=container_slug,
    )

    if container:
        container_service.check_container_status_for_start(
            container=container
        )
        result = container_service.change_container_status(
            config=config,
            container=container,
            action=ContainerPendingActionEnumDto.START
        )

        if result:
            typer.echo(__('Container will be started'))
        else:
            typer.echo(__('Something went wrong on server, please change late'))
    else:
        typer.echo(__("Not found container - %container_item%", {'container_item': container_slug}))

    app_logger.info(f'End start container')
    raise typer.Exit(0)


@app.command(name="stop", help=__("Help stop container"))
def item_stop(
        container_slug: Optional[str] = typer.Option(
            None,
            '--container-uniqueid',
            '-s',
            help=__("Container unique id"),
            is_eager=False,
        ),
        no_dialog: Optional[bool] = typer.Option(
            None,
            "--no-dialog",
            "-nd",
            help=__("Start process with default values, without future dialog"),
            is_eager=False,
        ),
):
    """
        Stop container
    """
    path = get_current_directory()
    app_logger.info(f'Stop container')

    if not container_slug:
        typer.echo(__('Container id or container slug is required'))
        raise typer.Exit(1)

    config, facade = base_global_check_validation(path=path, no_dialog=no_dialog)

    container_service: ContainerService = facade.get_container_service()

    container: Optional[DockerContainerDto] = container_service.get_item(
        config=config,
        container_slug=container_slug,
    )

    if container:
        container_service.check_container_status_for_stop(
            container=container
        )
        result = container_service.change_container_status(
            config=config,
            container=container,
            action=ContainerPendingActionEnumDto.STOP
        )

        if result:
            typer.echo(__('Container will be stoped'))
        else:
            typer.echo(__('Something went wrong on server, please change late'))
    else:
        typer.echo(__("Not found container - %container_item%", {'container_item': container_slug}))

    app_logger.info(f'End stop container')
    raise typer.Exit(0)
