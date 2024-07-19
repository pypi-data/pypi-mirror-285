from typing import Optional, Dict, Tuple, List

from thestage.services.clients.thestage_api.dtos.enums.rented_status import RentedStatusEnumDto
from thestage.i18n.translation import __
from thestage.services.storage.mapper.storage_mapper import StorageMapper
from thestage.services.storage.storage_service import StorageService
from thestage.controllers.utils_controller import get_current_directory, base_global_check_validation

import typer


app = typer.Typer(no_args_is_help=True, help=__("Help working with rented storages"))


@app.command(name="list")
def item_list(
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
        statuses: List[RentedStatusEnumDto] = typer.Option(
            ["RENTED"],
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
        List rented storages
    """
    path = get_current_directory()

    config, facade = base_global_check_validation(path=path, no_dialog=no_dialog)

    headers = ['#', 'SLUG', 'TITLE', 'PROVIDER ID', 'STATUS', 'IS ACTIVE', 'CREATED AT', 'UPDATED AT']

    storage_service: StorageService = facade.get_storage_service()

    typer.echo(__(
        "Start show rented storages list with statuses: %statuses% (You can show all statuses set up status=ALL)",
        placeholders={
            'statuses': ', '.join([item.value for item in statuses])
        }))

    if RentedStatusEnumDto.find_special_status(statuses=statuses):
        statuses = []

    storage_service.print(
        func_get_data=storage_service.get_list,
        func_special_params={
            'statuses': statuses,
        },
        mapper=StorageMapper(),
        config=config,
        headers=headers,
        row=row,
        page=page,
        no_dialog=no_dialog,
    )

    typer.echo(__("List storages done"))
    raise typer.Exit(0)
