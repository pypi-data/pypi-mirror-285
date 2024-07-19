import pathlib
from typing import Optional, Dict, Tuple

from thestage_core.entities.config_entity import ConfigEntity

from thestage.entities.enums.config_type import ConfigType
from thestage.helpers.error_handler import error_handler
from thestage.services.service_facade import ServiceFacade
from thestage.services.config_provider.config_provider import ConfigProvider


def get_current_directory() -> pathlib.Path:
    return pathlib.Path.cwd()


@error_handler()
def base_check_validation(
        path: str,
        working_directory: Optional[str] = None,
        no_dialog: bool = False,
) -> Tuple[ConfigEntity, ServiceFacade]:
    config_provider = ConfigProvider(project_path=path if not working_directory else working_directory)
    facade = ServiceFacade(config_provider=config_provider)
    config: ConfigEntity = config_provider.get_full_config()

    if no_dialog:
        config.runtime.config_type = ConfigType.LOCAL

    validation_service = facade.get_validation_service()
    validation_service.check_token(config=config, no_dialog=no_dialog)
    config_provider.save_full_config(config=config, config_type=config.runtime.config_type)
    return config, facade


@error_handler()
def base_global_check_validation(
        path: str,
        working_directory: Optional[str] = None,
        no_dialog: bool = False,
) -> Tuple[ConfigEntity, ServiceFacade]:
    config_provider = ConfigProvider(
        project_path=path if not working_directory else working_directory,
        auto_create=True,
        only_global=True,
    )
    facade = ServiceFacade(config_provider=config_provider)
    config: ConfigEntity = config_provider.get_full_config(only_global=True)

    validation_service = facade.get_validation_service()
    validation_service.check_token(config=config, no_dialog=no_dialog, only_global=True)
    config_provider.save_full_config(
        config=config,
        config_type=config.runtime.config_type
    )
    return config, facade
