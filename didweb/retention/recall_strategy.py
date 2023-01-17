import abc
import logging
from dataclasses import dataclass

from .storage_strategy import StorageStrategy

logger = logging.getLogger(__name__)


@dataclass
class RecallStrategyConfig:
    number_of_keys: int


class RecallStrategy(abc.ABC):
    async def previous_keys(self, did: str):
        """Return previous keys based on a set strategy"""


class NumberOfKeysStrategy(RecallStrategy):
    def __init__(self, storage_strategy: StorageStrategy, previous_keys: int = 0):
        self.__storage_strategy = storage_strategy
        self.__previous_keys = previous_keys

    async def previous_keys(self, did: str):
        all_previous_keys = await self.__storage_strategy.stored_keys(did)

        reversed_previous_keys = sorted(
            all_previous_keys, key=lambda previous_key: previous_key.index, reverse=True
        )

        logging.info(
            "Returning %s previous keys out of %s entries",
            self.__previous_keys,
            len(reversed_previous_keys),
        )
        return reversed_previous_keys[: self.__previous_keys]
