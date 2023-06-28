import json
from typing import Tuple, Type, Mapping
from unittest.mock import AsyncMock, MagicMock

import base58
import pytest
from aries_cloudagent.config.base import InjectType
from aries_cloudagent.core.profile import Profile, ProfileSession
from aries_cloudagent.protocols.coordinate_mediation.v1_0.route_manager import (
    RouteManager,
)
from aries_cloudagent.storage.base import BaseStorage
from aries_cloudagent.wallet.base import BaseWallet
from aries_cloudagent.wallet.did_info import DIDInfo
from aries_cloudagent.wallet.did_method import SOV
from aries_cloudagent.wallet.error import WalletNotFoundError
from aries_cloudagent.wallet.key_type import ED25519

from didmanagement import LatestVerificationKeyStrategy
from didmanagement.did_manager import DIDManager, RecallStrategyConfig, UnknownDIDException
from tests.conftest import DummyStorage


# Due to async context (async with), session is hard to mock using Async/MagicMock, so instead we create it manually
class MockSession(ProfileSession):
    def __init__(self, profile: Profile, storage: BaseStorage, wallet: BaseWallet):
        super().__init__(profile)
        self.__storage = storage
        self.__wallet = wallet

    def inject(
            self,
            base_cls: Type[InjectType],
            settings: Mapping[str, object] = None,
    ) -> InjectType:
        if base_cls == BaseWallet:
            return self.__wallet
        elif base_cls == BaseStorage:
            return self.__storage
        else:
            return None


@pytest.fixture
def a_did():
    yield DIDInfo(
        "did:sov:HR6vs6GEZ8rHaVgjg2WodM",
        base58.b58encode(b"a verification key").decode(),
        {},
        SOV,
        ED25519,
    )


@pytest.fixture
def mocked_wallet():
    mock_wallet = AsyncMock()
    mock_wallet.rotate_did_keypair_start = AsyncMock()
    mock_wallet.rotate_did_keypair_apply = AsyncMock()
    mock_wallet.get_local_did = AsyncMock()

    yield mock_wallet


def profile_with_config(config, routing_manager: RouteManager, storage: BaseStorage, wallet: BaseWallet):
    mock_profile = AsyncMock()
    mock_profile.inject = MagicMock(return_value=routing_manager)
    mock_profile.settings = config
    mock_session = MockSession(mock_profile, storage, wallet)
    mock_profile.session = MagicMock(return_value=mock_session)

    return mock_profile


@pytest.fixture
def configure_context(mocked_wallet):
    def configure_context(
        didinfo: DIDInfo,
        storage: DummyStorage,
        configured_endpoint: str = "http://endpoint.url",
        actual_endpoint: str = "http://endpoint.url",
    ) -> Tuple[Profile, BaseWallet]:
        dummy_profile = profile_with_config(
            {"default_endpoint": configured_endpoint},
            routing_manager=AsyncMock(
                routing_info=AsyncMock(return_value=([], actual_endpoint))
            ),
            storage=storage,
            wallet=mocked_wallet,
        )
        mocked_wallet.get_local_did.return_value = didinfo

        return dummy_profile, mocked_wallet

    yield configure_context


@pytest.mark.asyncio
async def test_get_diddoc_should_build_diddoc_with_correct_did_and_keys(
    a_did, configure_context, dummy_storage
):
    # given
    profile, wallet = configure_context(a_did, dummy_storage)

    # when
    didweb_manager = DIDManager(
        profile=profile,
        wallet=wallet,
        storage=dummy_storage,
        recall_strategy_config=RecallStrategyConfig(2),
    )

    diddoc = await didweb_manager.get_diddoc(a_did.did)
    parsed_json_document = json.loads(diddoc.to_json())

    # then
    assert parsed_json_document["id"] == a_did.did
    assert parsed_json_document["controller"] == [a_did.did]

    # verification methods
    verification_methods = parsed_json_document["verificationMethod"]
    assert len(verification_methods) == 1

    verification_method = verification_methods[0]
    assert verification_method["id"] == f"{a_did.did}#key-1"
    assert verification_method["controller"] == a_did.did
    assert verification_method["type"] == "Ed25519VerificationKey2018"
    assert verification_method["publicKeyBase58"] == a_did.verkey


@pytest.mark.asyncio
async def test_get_diddoc_should_populate_service(
    a_did, configure_context, dummy_storage
):
    # given
    expected_endpoint = "http://actual-endpoi.nt"
    profile, wallet = configure_context(a_did, dummy_storage, "http://configur.ed", expected_endpoint)

    # when
    didweb_manager = DIDManager(
        profile=profile,
        wallet=wallet,
        storage=dummy_storage,
        recall_strategy_config=RecallStrategyConfig(2),
    )

    diddoc = await didweb_manager.get_diddoc(a_did.did)
    parsed_json_document = json.loads(diddoc.to_json())

    # then
    assert len(parsed_json_document["service"]) == 1
    didcomm_service = parsed_json_document["service"][0]

    assert didcomm_service["id"] == f"{a_did.did}#service-0"
    assert didcomm_service["type"] == "did-communication"
    assert didcomm_service["recipientKeys"] == [f"{a_did.did}#key-1"]
    assert didcomm_service["serviceEndpoint"] == expected_endpoint
    assert didcomm_service["priority"] == 0


@pytest.mark.asyncio
async def test_get_diddoc_includes_relevant_contexts(
    a_did, configure_context, dummy_storage
):
    # given
    profile, wallet = configure_context(a_did, dummy_storage)

    # when
    didweb_manager = DIDManager(
        profile=profile,
        wallet=wallet,
        storage=dummy_storage,
        recall_strategy_config=RecallStrategyConfig(5),
    )

    await didweb_manager.rotate_key(a_did.did)
    diddoc = await didweb_manager.get_diddoc(a_did.did)
    parsed_json_document = json.loads(diddoc.to_json())

    # then
    assert len(parsed_json_document["verificationMethod"]) == 2

    contexts = parsed_json_document["@context"]
    assert "https://w3id.org/security/suites/ed25519-2018/v1" in contexts
    assert "https://www.w3.org/ns/did/v1" in contexts

    # check the contexts for duplicates
    assert len(set(contexts)) == len(contexts)


@pytest.mark.asyncio
async def test_rotate_key_should_use_underlying_wallet(
    a_did, configure_context, dummy_storage
):
    # given
    profile, wallet = configure_context(a_did, dummy_storage)

    # when
    didweb_manager = DIDManager(
        profile=profile,
        wallet=wallet,
        storage=dummy_storage,
        recall_strategy_config=RecallStrategyConfig(2),
    )

    diddoc = await didweb_manager.rotate_key(a_did.did)

    # then
    wallet.rotate_did_keypair_start.assert_called_once()
    wallet.rotate_did_keypair_apply.assert_called_once()

    contexts = json.loads(diddoc.to_json())["@context"]
    assert len(set(contexts)) == len(contexts)


@pytest.mark.asyncio
async def test_rotate_key_should_update_current_verkey_id(
        a_did, configure_context, dummy_storage
):
    profile, wallet = configure_context(a_did, dummy_storage)
    verkey_strat = LatestVerificationKeyStrategy()

    didweb_manager = DIDManager(
        profile=profile,
        wallet=wallet,
        storage=dummy_storage,
        recall_strategy_config=RecallStrategyConfig(2),
    )

    verkey_before_rotation = await verkey_strat.get_verification_method_id_for_did(a_did.did, profile)
    await didweb_manager.rotate_key(a_did.did)
    verkey_after_rotation = await verkey_strat.get_verification_method_id_for_did(a_did.did, profile)

    assert verkey_before_rotation == f"{a_did.did}#key-1"
    assert verkey_after_rotation == f"{a_did.did}#key-2"

@pytest.mark.asyncio
async def test_requests_for_unknown_did_should_fail(
       a_did, configure_context, dummy_storage
):
    profile, wallet = configure_context(a_did, dummy_storage)
    wallet.get_local_did.return_value = None
    wallet.get_local_did.side_effect = WalletNotFoundError("DID is unknown!")
    verkey_strat = LatestVerificationKeyStrategy()

    didweb_manager = DIDManager(
        profile=profile,
        wallet=wallet,
        storage=dummy_storage,
        recall_strategy_config=RecallStrategyConfig(2),
    )

    with pytest.raises(UnknownDIDException):
        await didweb_manager.get_diddoc("did:sov:unknown")

    verkey = await verkey_strat.get_verification_method_id_for_did("did:sov:unknown", profile)
    assert verkey is None
