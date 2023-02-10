from typing import List

import pytest

from didweb.retention import NumberOfKeysStrategy, StorageStrategy, PreviousKey


class DummyStorageStrategy(StorageStrategy):
    def __init__(self, keys: List[PreviousKey]):
        self.__stored_keys = keys

    async def stored_keys(self, did: str) -> List[PreviousKey]:
        return self.__stored_keys


def get_dummy_keys(n: int) -> List[PreviousKey]:
    return [PreviousKey(i, b"abc") for i in range(n)]


@pytest.mark.parametrize(
    "stored_keys, requested_keys",
    (
        ([], 2),
        (get_dummy_keys(2), 2),
        (get_dummy_keys(3), 2),
        (get_dummy_keys(2), 3),
    ),
)
@pytest.mark.asyncio
async def test_number_of_keys_strategy_returns_at_most_requested_number_of_keys(
    stored_keys, requested_keys
):
    # given
    storage_strategy = DummyStorageStrategy(stored_keys)

    # when
    recall_strategy = NumberOfKeysStrategy(storage_strategy, requested_keys)
    recalled_keys = await recall_strategy.previous_keys("did:phone:911")

    # then
    assert len(recalled_keys) == min(len(stored_keys), requested_keys)


@pytest.mark.asyncio
async def test_number_of_keys_strategy_returns_keys_in_descending_order_of_creation():
    # given
    stored_keys = [
        PreviousKey(3, b"abc"),
        PreviousKey(1, b"abc"),
        PreviousKey(5, b"abc"),
        PreviousKey(2, b"abc"),
    ]

    storage_strategy = DummyStorageStrategy(stored_keys)

    # when
    recall_strategy = NumberOfKeysStrategy(storage_strategy, len(stored_keys))
    recalled_keys = await recall_strategy.previous_keys("did:phone:911")

    # then
    assert recalled_keys == sorted(stored_keys, key=lambda k: k.index, reverse=True)
