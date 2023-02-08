import abc
import base64
import logging
from typing import List

from aries_cloudagent.storage.base import BaseStorage
from aries_cloudagent.storage.record import StorageRecord

from .previous_key import PreviousKey


PREVIOUS_PUBLIC_KEY_RECORD_TYPE = "PREVIOUS_PUBLIC_KEY"
logger = logging.getLogger(__name__)


class StorageStrategy(abc.ABC):
    async def stored_keys(self, did: str) -> List[PreviousKey]:
        """retrieve all previous keys valid for the current strategy"""

    async def store_old_key(self, did: str, signing_key: bytes):
        """Store a key as a "previous" key."""

    async def current_index(self, did: str) -> int:
        """
        Return the index for the currently in-use key based on the key history.
        :param did:
        :return:
        """


class AskarStorageStrategy(StorageStrategy):
    def __init__(self, storage: BaseStorage):
        """
        :param storage:
        """
        self.__storage = storage

    async def stored_keys(self, did) -> List[PreviousKey]:
        previous_keys = await self.__storage.find_all_records(
            PREVIOUS_PUBLIC_KEY_RECORD_TYPE, {"did": did}
        )

        return [
            PreviousKey(int(key.tags.get("index")), base64.b64decode(key.value))
            for key in previous_keys
        ]

    async def store_old_key(self, did: str, signing_key: bytes):
        """
        :param did: DID for which the key is being safe-kept
        :param signing_key: bytes of the DID's signing key
        :return:
        """
        # Store current key
        # record: (type, value, tags, id)
        index = await self.current_index(did)
        logger.info("Storing key %s with index %s for did %s", did, index, signing_key)

        current_key_record = StorageRecord(
            PREVIOUS_PUBLIC_KEY_RECORD_TYPE,
            base64.b64encode(signing_key),
            {"did": did, "index": str(index)},
            f"{did}#{index}",
        )
        await self.__storage.add_record(current_key_record)

    async def current_index(self, did: str) -> int:
        previous_keys = await self.stored_keys(did)

        if previous_keys is None:
            logger.error("Previous keys: %s", previous_keys)
            raise ValueError("Provide a did or a list of previous keys")

        indices = [key.index for key in previous_keys]
        return max(indices) + 1 if len(previous_keys) > 0 else 1


class NoStorageStrategy(StorageStrategy):
    async def stored_keys(self, did: str) -> List[PreviousKey]:
        """retrieve all previous keys valid for the current strategy"""
        return list()

    async def current_index(self, did: str) -> int:
        """
        Return the index for the currently in-use key based on the key history.
        """
        return 1
