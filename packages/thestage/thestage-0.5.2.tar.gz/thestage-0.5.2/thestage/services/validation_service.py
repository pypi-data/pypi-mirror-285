from typing import Dict, Optional

import typer
from thestage_core.entities.config_entity import ConfigEntity, MainConfigEntity
from thestage_core.services.validation_service import ValidationServiceCore

from thestage.i18n.translation import __
from thestage.services.clients.thestage_api.dtos.user_profile import UserProfileResponse
from thestage.entities.enums.config_type import ConfigType
from thestage.services.config_provider.config_provider import ConfigProvider
from thestage.services.clients.thestage_api.api_client import TheStageApiClient


class ValidationService(ValidationServiceCore):
    _thestage_api_client: TheStageApiClient = None

    def __init__(
            self,
            thestage_api_client: TheStageApiClient,
            config_provider: ConfigProvider,
    ):
        super(ValidationService, self).__init__(
            thestage_api_client=thestage_api_client,
            config_provider=config_provider,
        )

    def check_token(
            self,
            config: ConfigEntity,
            no_dialog: bool = False,
            only_global: bool = False,
    ):

        is_present = self.is_present_token(config=config)

        token = config.main.auth_token if config and config.main else None
        if not is_present:

            if no_dialog:
                typer.echo(__(
                    'In no dialog mode, you need added token to config or to system env: TSR_AUTH_TOKEN'
                ))
                raise typer.Exit(1)

            new_token: str = typer.prompt(
                text=__('Please sign in via valid TheStage.ai API token'),
                show_choices=False,
                type=str,
                show_default=False,
            )
            token = new_token

        is_valid = self.validate_token(token,)
        if not is_valid:
            typer.echo(__(
                'Please issue the valid API token in your TheStage.ai web app account'
            ))
            raise typer.Exit(1)

        typer.echo(__('Token is valid'))
        if not is_present:
            if only_global:
                config.runtime.config_type = ConfigType.GLOBAL
            else:
                config_type: ConfigType = typer.prompt(
                    text=__('Where you want to save token (LOCAL or GLOBAL config)'),
                    show_choices=True,
                    default=ConfigType.LOCAL.value,
                    type=ConfigType,
                    show_default=True,
                )

                config.runtime.config_type = config_type

            if config.main:
                config.main.auth_token = token
            else:
                config.main = MainConfigEntity(tsr_auth_token=token)

    def get_profile(self, token: str) -> Optional[UserProfileResponse]:
        return self.__thestage_api_client.get_profile(token=token)
