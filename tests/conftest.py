from typing import Mapping

import pytest
from aries_cloudagent.storage.base import BaseStorage
from aries_cloudagent.storage.record import StorageRecord


class DummyStorage(BaseStorage):
    def __init__(self):
        self.store = dict()

    async def add_record(self, record: StorageRecord):
        self.store[record.id] = record

    async def get_record(
        self, record_type: str, record_id: str, options: Mapping = None
    ) -> StorageRecord:
        return self.store[record_id]

    async def find_all_records(
        self, type_filter: str, tag_query: Mapping = None, options: Mapping = None
    ):
        return [v for v in self.store.values()]

    async def update_record(self, record: StorageRecord, value: str, tags: Mapping):
        pass

    async def delete_record(self, record: StorageRecord):
        pass

    async def delete_all_records(self, type_filter: str, tag_query: Mapping = None):
        pass


@pytest.fixture
def dummy_storage():
    yield DummyStorage()
