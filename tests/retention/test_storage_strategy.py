import pytest

from didweb.retention import NoStorageStrategy, StorageBackendStorageStrategy, PreviousKey


@pytest.mark.asyncio
async def test_storage_backend_strategy_stores_keys_and_recall_with_index(dummy_storage):
    # given
    did = "did:phone:911"

    # when
    storage = StorageBackendStorageStrategy(dummy_storage)
    await storage.store_old_key(did, b"abc")

    # then
    assert await storage.stored_keys(did) == [PreviousKey(1, b"abc")]


@pytest.mark.asyncio
async def test_storage_backend_strategy_retrieves_correct_index(dummy_storage):
    # given
    did = "did:phone:911"

    # when
    storage = StorageBackendStorageStrategy(dummy_storage)
    await storage.store_old_key(did, b"abc")
    await storage.store_old_key(did, b"def")

    # then
    assert await storage.current_index(did) == 3


@pytest.mark.asyncio
async def test_no_storage_strategy_never_stores_keys():
    # given
    did = "did:phone:911"

    # when - then
    storage = NoStorageStrategy()

    assert await storage.store_old_key(did, b"abc") is None
    assert await storage.stored_keys(did) == []
    assert await storage.current_index(did) == 1
