from abc import ABC
from typing import List, Dict, Any

import typer
from tabulate import tabulate
from thestage_core.entities.config_entity import ConfigEntity

from thestage.i18n.translation import __
from thestage.services.config_provider.config_provider import ConfigProvider
from thestage.services.storage.mapper.storage_mapper import AbstractMapper


class AbstractService(ABC):

    def __init__(
            self,
            config_provider: ConfigProvider,
    ):
        self._config_provider = config_provider

    def print(
            self,
            func_get_data,
            func_special_params: Dict[str, Any],
            mapper: AbstractMapper,
            config: ConfigEntity,
            headers: List[str],
            row: int = 5,
            page: int = 1,
            no_dialog: bool = False,
            show_index: str = 'always',
            max_col_width: List[int] = None,
    ):
        data, total_pages = func_get_data(
            config=config,
            row=row,
            page=page,
            **func_special_params,
        )

        result = list(map(lambda x: mapper.build_entity(x), data))

        if result:
            raw_data = [list(item.model_dump(
                by_alias=True,
                exclude=mapper.get_exclude_fields(),
            ).values()) for item in result]
        else:
            raw_data = [[] for item in headers]
            show_index = 'never'

        typer.echo(__(
            "Page: %page%, Limit: %limit%, Total page: %total_pages%",
            {
                'page': str(page),
                'limit': str(row),
                'total_pages': str(total_pages),
            }
        ))

        typer.echo(tabulate(
            raw_data,
            headers=headers,
            showindex=show_index,
            tablefmt="double_grid",
            #headers="firstrow",
            maxcolwidths=max_col_width,
        ))

        if len(raw_data) == 1:
            typer.echo(__("List empty, work done"))
            raise typer.Exit(0)

        if no_dialog:
            raise typer.Exit(0)

        next_page: int = typer.prompt(
            text=__('Go to next page (0 to exit)?'),
            default=page + 1,
            show_choices=False,
            type=int,
            show_default=True,
        )
        if next_page == 0:
            raise typer.Exit(0)
        else:
            self.print(
                func_get_data=func_get_data,
                func_special_params=func_special_params,
                mapper=mapper,
                config=config,
                headers=headers,
                row=row,
                page=next_page,
                no_dialog=no_dialog,
            )
