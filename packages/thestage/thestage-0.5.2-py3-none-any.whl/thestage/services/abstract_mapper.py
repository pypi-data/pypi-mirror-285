from abc import ABC
from typing import Any, Optional, Tuple


class AbstractMapper(ABC):

    @staticmethod
    def get_exclude_fields() -> Tuple:
        return ()

    @staticmethod
    def build_entity(item: Any) -> Optional[Any]:
        raise NotImplementedError()
