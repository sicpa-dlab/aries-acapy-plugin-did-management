import json
from typing import Tuple
from unittest.mock import AsyncMock, MagicMock

import base58
import pytest
from aries_cloudagent.core.profile import Profile
from aries_cloudagent.protocols.coordinate_mediation.v1_0.route_manager import (
    RouteManager,
)
from aries_cloudagent.wallet.base import BaseWallet
from aries_cloudagent.wallet.did_info import DIDInfo
from aries_cloudagent.wallet.key_type import ED25519

from didweb import WEB
from didweb.didweb_manager import DIDWebManager, RecallStrategyConfig


@pytest.fixture
def a_did():
    yield DIDInfo(
        "did:web:perdu.com",
        base58.b58encode(b"a verification key").decode(),
        {},
        WEB,
        ED25519,
    )


@pytest.fixture
def mocked_wallet():
    mock_wallet = AsyncMock()
    mock_wallet.rotate_did_keypair_start = AsyncMock()
    mock_wallet.rotate_did_keypair_apply = AsyncMock()
    mock_wallet.get_local_did = AsyncMock()

    yield mock_wallet


def profile_with_config(config, routing_manager: RouteManager):
    mock_profile = AsyncMock()
    mock_profile.inject = MagicMock(return_value=routing_manager)
    mock_profile.settings = config

    return mock_profile


@pytest.fixture
def configure_context(mocked_wallet):
    def configure_context(
        didinfo: DIDInfo,
        configured_endpoint: str = "http://endpoint.url",
        actual_endpoint: str = "http://endpoint.url",
    ) -> Tuple[Profile, BaseWallet]:
        dummy_profile = profile_with_config(
            {"default_endpoint": configured_endpoint},
            routing_manager=AsyncMock(
                routing_info=AsyncMock(return_value=([], actual_endpoint))
            ),
        )
        mocked_wallet.get_local_did.return_value = didinfo

        return dummy_profile, mocked_wallet

    yield configure_context


@pytest.mark.asyncio
async def test_get_diddoc_should_build_diddoc_with_correct_did_and_keys(
    a_did, configure_context, dummy_storage
):
    # given
    profile, wallet = configure_context(a_did)

    # when
    didweb_manager = DIDWebManager(
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
    profile, wallet = configure_context(a_did, "http://configur.ed", expected_endpoint)

    # when
    didweb_manager = DIDWebManager(
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
async def test_rotate_key_should_use_underlying_wallet(
    a_did, configure_context, dummy_storage
):
    # given
    profile, wallet = configure_context(a_did)

    # when
    didweb_manager = DIDWebManager(
        profile=profile,
        wallet=wallet,
        storage=dummy_storage,
        recall_strategy_config=RecallStrategyConfig(2),
    )

    await didweb_manager.rotate_key(a_did.did)

    # then
    wallet.rotate_did_keypair_start.assert_called_once()
    wallet.rotate_did_keypair_apply.assert_called_once()
