from typing import List, Tuple, Optional

from thestage_core.entities.config_entity import ConfigEntity

from thestage.services.clients.thestage_api.dtos.enums.rented_status import RentedStatusEnumDto
from thestage.services.clients.thestage_api.dtos.storage_rented_response import StorageRentedDto
from thestage.services.abstract_service import AbstractService
from thestage.helpers.error_handler import error_handler
from thestage.services.clients.thestage_api.api_client import TheStageApiClient
from thestage.services.config_provider.config_provider import ConfigProvider


class StorageService(AbstractService):

    __thestage_api_client: TheStageApiClient = None

    def __init__(
            self,
            thestage_api_client: TheStageApiClient,
            config_provider: ConfigProvider,
    ):
        super(StorageService, self).__init__(
            config_provider=config_provider
        )

        self.__thestage_api_client = thestage_api_client

    @error_handler()
    def get_list(
            self,
            config: ConfigEntity,
            statuses: List[RentedStatusEnumDto],
            row: int = 5,
            page: int = 1,
    ) -> Tuple[List[StorageRentedDto], int]:

        data, total_pages = self.__thestage_api_client.get_rented_storage_list(
            token=config.main.auth_token,
            statuses=statuses,
            page=page,
            limit=row,
        )

        return data, total_pages
