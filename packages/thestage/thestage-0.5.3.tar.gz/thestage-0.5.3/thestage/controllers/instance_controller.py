from typing import Optional, List

from thestage.helpers.logger.app_logger import app_logger
from thestage.services.clients.thestage_api.dtos.enums.selfhosted_status import SelfHostedStatusEnumDto, \
    SelfHostedBusinessStatusEnumDto
from thestage.services.clients.thestage_api.dtos.enums.rented_status import RentedStatusEnumDto, \
    RentedBusinessStatusEnumDto
from thestage.services.instance.mapper.instance_mapper import InstanceMapper
from thestage.services.instance.mapper.selfhosted_mapper import SelfHostedMapper
from thestage.services.instance.instance_service import InstanceService
from thestage.i18n.translation import __
from thestage.controllers.utils_controller import get_current_directory, base_global_check_validation

import typer


app = typer.Typer(no_args_is_help=True, help=__("Help working with instances"))

rented = typer.Typer(no_args_is_help=True, help=__("Help working with rented instances"))
self_hosted = typer.Typer(no_args_is_help=True, help=__("Help working with self hosted instances"))

app.add_typer(rented, name="rented")
app.add_typer(self_hosted, name="self-hosted")


@rented.command(name="ls", help=__("Show list rented instances"))
def rented_list(
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
        statuses: List[RentedBusinessStatusEnumDto] = typer.Option(
            ["ONLINE", "IN_QUEUE", "CREATING", "TERMINATING", "REBOOTING"],
            '--status',
            '-s',
            help=__("Status item (ALL - show all instances)"),
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
        List rented instances
    """
    path = get_current_directory()
    config, facade = base_global_check_validation(path=path, no_dialog=no_dialog)

    headers = [
        #'#',
        #'ID',
        'STATUS',
        'TITLE',
        'UNIQUE ID',
        'CPU TYPE',
        'CPU CORES',
        'GPU TYPE',
        'IP ADDRESS',
        'CREATED AT',
        'UPDATED AT',
    ]

    instance_service: InstanceService = facade.get_instance_service()

    typer.echo(__(
        "Start show instance list with statuses: %statuses% (You can show all statuses set up status=ALL)",
        placeholders={
            'statuses': ', '.join([item.value for item in statuses])
        }))

    if RentedBusinessStatusEnumDto.find_special_status(statuses=statuses):
        statuses = []

    instance_service.print(
        func_get_data=instance_service.get_rented_list,
        func_special_params={
            'statuses': statuses,
        },
        mapper=InstanceMapper(),
        config=config,
        headers=headers,
        row=row,
        page=page,
        no_dialog=no_dialog,
        show_index="never",
    )

    typer.echo(__("List rented done"))
    raise typer.Exit(0)


@rented.command(name="connect", help=__("Help connect to instance"))
def instance_connect(
        instance_slug: Optional[str] = typer.Option(
            None,
            '--instance-uniqueid',
            '-s',
            help=__("Instance unique id"),
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
        Connect to instance
    """
    path = get_current_directory()
    app_logger.info(f'Connect to instance')

    if not instance_slug:
        typer.echo(__('Instance unique id is required'))
        raise typer.Exit(1)

    config, facade = base_global_check_validation(path=path, no_dialog=no_dialog)

    instance_service: InstanceService = facade.get_instance_service()
    instance = instance_service.get_rented_item(config=config, instance_slug=instance_slug)

    if instance:
        instance_service.check_instance_status_to_connect(
            instance=instance,
        )
        instance_service.connect_to_instance(
            ip_address=instance.ip_address,
            username=instance.host_username,
        )
    else:
        typer.echo(__("Not found instance - %instance_item%", {'instance_item': instance_slug}))

    app_logger.info(f'Stop connect to instance')
    raise typer.Exit(0)


@self_hosted.command(name="ls", help=__("Show list self-hosted instances"))
def self_hosted_list(
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
        statuses: List[SelfHostedBusinessStatusEnumDto] = typer.Option(
            ["AWAITING_CONFIGURATION", "RUNNING", "TERMINATED"],
            '--status',
            '-s',
            help=__("Status item (ALL - show all instances)"),
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
        List self hosted instances
    """
    path = get_current_directory()
    config, facade = base_global_check_validation(path=path, no_dialog=no_dialog)

    headers = [
        # '#',
        # 'ID',
        'STATUS',
        'TITLE',
        'UNIQUE ID',
        'CPU TYPE',
        'CPU CORES',
        'GPU TYPE',
        'IP ADDRESS',
        'CREATED AT',
        'UPDATED AT'
    ]

    instance_service: InstanceService = facade.get_instance_service()

    typer.echo(__(
        "Start show self-hosted list with statuses: %statuses% (You can show all statuses set up status=ALL)",
        placeholders={
            'statuses': ', '.join([item.value for item in statuses])
        }))

    if SelfHostedBusinessStatusEnumDto.find_special_status(statuses=statuses):
        statuses = []

    instance_service.print(
        func_get_data=instance_service.get_self_hosted_list,
        func_special_params={
            'statuses': statuses,
        },
        mapper=SelfHostedMapper(),
        config=config,
        headers=headers,
        row=row,
        page=page,
        no_dialog=no_dialog,
        show_index="never",
    )

    typer.echo(__("List self-hosted done"))
    raise typer.Exit(0)


@self_hosted.command(name="connect", help=__("Help connect to self hosted"))
def self_hosted_connect(
        instance_slug: Optional[str] = typer.Option(
            None,
            '--instance-uniqueid',
            '-s',
            help=__("Instance unique id"),
            is_eager=False,
        ),
        username: Optional[str] = typer.Option(
            'root',
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
        Connect to self hosted instances
    """
    path = get_current_directory()
    app_logger.info(f'Connect to self hosted instance')

    if not instance_slug:
        typer.echo(__('Instance unique id is required'))
        raise typer.Exit(1)

    config, facade = base_global_check_validation(path=path, no_dialog=no_dialog)

    instance_service: InstanceService = facade.get_instance_service()
    # rebuild to rented
    instance = instance_service.get_self_hosted_item(config=config, instance_slug=instance_slug)

    if instance:
        instance_service.check_selfhosted_status_to_connect(
            instance=instance,
        )

        if not username or not instance.host_username:
            typer.echo(__('Not found user connect ti instance'))
            raise typer.Exit(1)

        instance_service.connect_to_instance(
            ip_address=instance.ip_address,
            username=username or instance.host_username or 'root',
        )
    else:
        typer.echo(__("Not found instance - %instance_item%", {'instance_item': instance_slug}))

    app_logger.info(f'Stop connect to instance')
    raise typer.Exit(0)
