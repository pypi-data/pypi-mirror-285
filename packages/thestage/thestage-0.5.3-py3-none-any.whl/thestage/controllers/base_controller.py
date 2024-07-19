
from thestage.i18n.translation import __
from thestage.helpers.logger.app_logger import app_logger
from thestage.controllers.utils_controller import base_check_validation, get_current_directory
from thestage import __app_name__, __version__

import typer

app = typer.Typer(no_args_is_help=True)


@app.command(no_args_is_help=False)
def version():
    """
        return Name and Version app
    """
    path = get_current_directory()
    app_logger.info(f'Start version from {path}')
    typer.echo(
        __("%app_name% v%version%", {'app_name': __app_name__, 'version': __version__}))
    raise typer.Exit(0)
