import os
from typing import Any, Callable

import typer
from click.exceptions import Exit
from git import GitCommandError

from thestage.config import THESTAGE_API_URL
from thestage.exceptions.remote_server_exception import RemoteServerException
from thestage.i18n.translation import __
from thestage.exceptions.git_access_exception import GitAccessException
from thestage.exceptions.auth_exception import AuthException
from thestage.exceptions.business_logic_exception import BusinessLogicException
from thestage.exceptions.config_exception import ConfigException
from thestage.exceptions.file_system_exception import FileSystemException
from thestage.exceptions.http_error_exception import HttpClientException
from thestage.helpers.logger.app_logger import app_logger


def error_handler() -> Callable:
    def wrap(f):
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                result = f(*args, **kwargs)
                return result
            except AuthException as e1:
                typer.echo(__('Auth exception, change token'))
                app_logger.ex(f"Auth exception, change token - {e1}")
                raise typer.Exit(1)
            except BusinessLogicException as e2:
                typer.echo(__('We have error on business logic, please connect with developer'))
                app_logger.info(f"We have error on business logic, please connect with developer - {e2}")
                raise typer.Exit(1)
            except ConfigException as e3:
                typer.echo(__(
                    'We have error on working with config - %error_message%',
                    {
                        'error_message': e3.get_message()
                    }
                ))
                app_logger.info(f"We have error on working with config - {e3}")
                raise typer.Exit(1)
            except FileSystemException as e4:
                typer.echo(__(
                    "We have error on working with file system - %error_message%",
                    {
                        'error_message': e4.get_message()
                    }
                ))
                app_logger.info(f'We have error on working with file system - {e4}')
                raise typer.Exit(1)
            except HttpClientException as e5:
                typer.echo(__(
                    f"Error connect to the %stage_url%. %error_message%",
                    {
                        'stage_url': THESTAGE_API_URL,
                        'error_message': e5.get_message()
                    }
                ))
                app_logger.info(f"Error connect to the {THESTAGE_API_URL} - {e5}")
                raise typer.Exit(1)
            except GitAccessException as e6:
                typer.echo(e6.get_message())
                typer.echo(e6.get_dop_message())
                typer.echo(__(
                    "Please open this repo url %git_url% and 'Accept invitation', or check your access to repository",
                    {
                        'git_url': e6.get_url(),
                    }
                ))
                raise typer.Exit(1)
            except GitCommandError as e7:
                typer.echo(__(
                    "Error git command - %git_status% - %git_error%",
                    {
                        'git_status': e7.status,
                        'git_error': e7.stderr,
                    }
                ))
                app_logger.info(f"Error git command - {e7}")
                raise typer.Exit(1)
            except RemoteServerException as e8:
                typer.echo(__(
                    'Error connect to server or docker container %ip_address% by %username%',
                    {
                        'ip_address': e8.ip_address,
                        'username': e8.username,
                    }))
                app_logger.info(f'Error connect to server or docker container {e8.ip_address} by {e8.username} - {e8}')
                raise typer.Exit(1)
            except Exception as e100:
                if isinstance(e100, Exit):
                    raise e100
                else:
                    typer.echo(__('Undefined utility error'))
                    typer.echo(e100)
                    app_logger.info(f'Undefined utility error - {e100}')
                    raise typer.Exit(1)

        return wrapper
    return wrap
