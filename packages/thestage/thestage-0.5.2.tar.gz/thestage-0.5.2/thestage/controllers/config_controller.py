from thestage_core.entities.config_entity import ConfigEntity

from thestage.i18n.translation import __
from thestage.helpers.logger.app_logger import app_logger
from thestage.services.config_provider.config_provider import ConfigProvider
from thestage.services.service_facade import ServiceFacade
from thestage.controllers.utils_controller import base_check_validation, get_current_directory

import typer

app = typer.Typer(no_args_is_help=True, help=__("Help working with config"))


@app.command(name='get', no_args_is_help=False, help=__("Print all config items"))
def config_get():
    """
        Print all use configs
    """
    path = get_current_directory()
    app_logger.info(f'Start config from {path}')

    config_provider = ConfigProvider(
        project_path=path,
        only_global=True,
    )
    facade = ServiceFacade(config_provider=config_provider)
    config: ConfigEntity = config_provider.get_full_config(only_global=True)

    if not config:
        typer.echo(__('You dont have config yet'))
        raise typer.Exit(1)

    typer.echo(__('THESTAGE TOKEN: %token%', {'token': config.main.auth_token or ''}))
    typer.echo(__('THESTAGE CONFIG FILE: %dir%', {'dir': config.main.config_file_name or ''}))
    typer.echo(__('THESTAGE API LINK: %link%', {'link': config.main.config_api_link or ''}))
    if config.main.config_local_path:
        typer.echo(__('THESTAGE LOCAL CONFIG PATH: %path%', {'path': str(config.main.config_local_path or '')}))
    if config.main.config_global_path:
        typer.echo(__('THESTAGE GLOBAL CONFIG PATH: %path%', {'path': str(config.main.config_global_path or '')}))

    raise typer.Exit(0)


@app.command(name='set', no_args_is_help=True, help=__("Set some config item"))
def config_set(
    token: str = typer.Option(
            None,
            "--api-token",
            "-t",
            help=__("If you want initialize or change token"),
            is_eager=False,
            is_flag=True,
        ),
):
    """
        Set up some params
    """
    path = get_current_directory()
    app_logger.info(f'Start config from {path}')

    config_provider = ConfigProvider(
        project_path=path,
        only_global=True,
    )
    facade = ServiceFacade(config_provider=config_provider)
    config: ConfigEntity = config_provider.get_full_config(only_global=True)
    app_service = facade.get_app_config_service()

    if token:
        app_service.app_change_token(config=config, token=token, only_global=True)

    typer.echo('Config changed')
    raise typer.Exit(0)


@app.command(name='clear', no_args_is_help=False, help=__("Clear thestage config"))
def config_clear():
    """
        Clear config
    """
    path = get_current_directory()
    app_logger.info(f'Start config from {path}')

    config_provider = ConfigProvider(
        project_path=path,
        only_global=True,
    )
    facade = ServiceFacade(config_provider=config_provider)
    config_provider.remove_all_config()

    raise typer.Exit(0)
