import base64
from dataclasses import dataclass
from typing import Iterable, Tuple, List, cast

import base58
from aries_cloudagent.core.profile import Profile
from aries_cloudagent.did.did_key import DIDKey
from aries_cloudagent.protocols.coordinate_mediation.v1_0.route_manager import (
    RouteManager,
)
from aries_cloudagent.storage.base import BaseStorage
from aries_cloudagent.wallet.base import BaseWallet
from aries_cloudagent.wallet.did_info import DIDInfo
from aries_cloudagent.wallet.key_type import ED25519

from pydid import DIDDocumentBuilder, DIDUrl
from pydid.verification_method import JsonWebKey2020, VerificationMethod

from didweb.retention import AskarStorageStrategy, NumberOfKeysStrategy


class UnknownDIDException(Exception):
    """When trying to operate on an unknown DID."""


@dataclass
class RecallStrategyConfig:
    number_of_keys: int = 0


class DIDWebManager:
    def __init__(
        self,
        profile: Profile,
        wallet: BaseWallet,
        storage: BaseStorage,
        recall_strategy_config: RecallStrategyConfig = None,
    ):
        self.__profile = profile
        self.__wallet = wallet
        self.__storage = storage
        self.__storage_strategy = AskarStorageStrategy(self.__storage)
        self.__recall_strategy = (
            NumberOfKeysStrategy(
                self.__storage_strategy, recall_strategy_config.number_of_keys
            )
            if recall_strategy_config
            else NumberOfKeysStrategy(self.__storage_strategy, 0)
        )

    async def get_diddoc(self, did: str):
        """
        Generate a DIDDocument for a given DID
        :param did:
        :return: a w3c compliant DID Document
        """

        # fetch did with current key
        did_info, signing_key_b64 = await self._get_did_and_signing_key(did)
        if not did_info:
            raise UnknownDIDException()

        # Also retrieve n previous keys and build complete key list
        previous_keys = await self.__recall_strategy.previous_keys(did)
        keys_with_indices = [
            (await self.__storage_strategy.current_index(did), signing_key_b64)
        ]
        keys_with_indices.extend(
            [(previous_key.index, previous_key.key) for previous_key in previous_keys]
        )

        # Build diddoc
        did_doc_builder = DIDDocumentBuilder(did, controller=[did])

        verification_methods = _build_verification_methods(did, keys_with_indices)
        did_doc_builder.verification_method.methods.extend(verification_methods)

        # reference the keys in the other sections
        all_key_references = _build_key_references(did, keys_with_indices)
        did_doc_builder.authentication.methods.extend(all_key_references)

        # add routing information
        routing_keys, endpoint = await self._retrieve_routing_information()
        did_doc_builder.service.add_didcomm(
            endpoint,
            recipient_keys=[did_doc_builder.verification_method.methods[0]],
            routing_keys=[
                DIDKey.from_public_key_b58(key, key_type=ED25519).did
                for key in routing_keys
            ],
        )

        return did_doc_builder.build()

    async def rotate_key(self, did: str):
        # Safe keep the old key
        did_info, signing_key_b64 = await self._get_did_and_signing_key(did)
        await self.__storage_strategy.store_old_key(did, signing_key_b64)

        # Rotate key in wallet
        await self.__wallet.rotate_did_keypair_start(did)
        await self.__wallet.rotate_did_keypair_apply(did)

        # Return new DIDDoc
        return await self.get_diddoc(did)

    async def _get_did_and_signing_key(self, did) -> Tuple[DIDInfo, bytes]:
        did_info = await self.__wallet.get_local_did(did)
        signing_key_b64 = base64.b64encode(base58.b58decode(did_info.verkey))

        return did_info, signing_key_b64

    async def _retrieve_routing_information(self) -> Tuple[List[str], str]:
        route_manager = self.__profile.inject(RouteManager)
        routing_keys, my_endpoint = await route_manager.routing_info(
            self.__profile,
            cast(str, self.__profile.settings.get("default_endpoint")),
            None,
        )
        return routing_keys, my_endpoint


def _build_verification_methods(
    did: str, keys_with_indices: Iterable[Tuple[int, bytes]]
) -> List[VerificationMethod]:
    return [
        JsonWebKey2020(
            id=f"{did}#key-{index}",
            type="JsonWebKey2020",
            controller=did,
            public_key_jwk={
                "kty": "OKP",
                # TODO: remove hard-coding if we want to support more key types
                "crv": "Ed25519",
                "x": signing_key,
            },
        )
        for index, signing_key in keys_with_indices
    ]


def _build_key_references(
    did: str, keys_with_indices: Iterable[Tuple[int, bytes]]
) -> List[DIDUrl]:
    return [DIDUrl(f"{did}#key-{index}") for index, _ in keys_with_indices]
