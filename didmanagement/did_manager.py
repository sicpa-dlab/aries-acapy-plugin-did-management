import logging
from dataclasses import dataclass
import itertools
from typing import Iterable, Tuple, List, cast, Callable

import base58
from aries_cloudagent.core.profile import Profile
from aries_cloudagent.did.did_key import DIDKey
from aries_cloudagent.protocols.coordinate_mediation.v1_0.route_manager import (
    RouteManager,
)
from aries_cloudagent.storage.base import BaseStorage
from aries_cloudagent.wallet.base import BaseWallet
from aries_cloudagent.wallet.did_info import DIDInfo
from aries_cloudagent.wallet.error import WalletNotFoundError
from aries_cloudagent.wallet.key_type import ED25519

from pydid import DIDDocumentBuilder, DIDUrl
from pydid.verification_method import VerificationMethod

from didmanagement.retention import StorageBackendStorageStrategy, NumberOfKeysStrategy
from didmanagement.verification_methods import Did, ed25519_verification_key_2018


class UnknownDIDException(Exception):
    """When trying to operate on an unknown DID."""


@dataclass
class RecallStrategyConfig:
    number_of_keys: int = 0


class DIDManager:
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
        self.__storage_strategy = StorageBackendStorageStrategy(self.__storage)
        self.__recall_strategy = (
            NumberOfKeysStrategy(
                self.__storage_strategy, recall_strategy_config.number_of_keys
            )
            if recall_strategy_config
            else NumberOfKeysStrategy(self.__storage_strategy, 0)
        )

        self.__verification_method_factory = ed25519_verification_key_2018

    async def get_diddoc(
        self,
        did: str,
        verification_method_factory: Callable[
            [Did, int, bytes], VerificationMethod
        ] = None,
    ):
        """
        Generate a DIDDocument for a given DID
        :param did:
        :param verification_method_factory:
        :return: a w3c compliant DID Document
        """
        verification_method_factory = (
            self.__verification_method_factory
            if verification_method_factory is None
            else verification_method_factory
        )

        # fetch did with current key
        did_info, signing_key = await self._get_did_and_signing_key(did)

        # Also retrieve n previous keys and build complete key list
        previous_keys = await self.__recall_strategy.previous_keys(did)
        keys_with_indices = [
            (await self.__storage_strategy.current_index(did), signing_key)
        ]
        keys_with_indices.extend(
            [(previous_key.index, previous_key.key) for previous_key in previous_keys]
        )

        # Build diddoc
        did_doc_builder = DIDDocumentBuilder(did, controller=[did])

        verification_methods_and_contexts = [
            verification_method_factory(did, key_index, key)
            for key_index, key in keys_with_indices
        ]
        verification_methods, contexts = zip(*verification_methods_and_contexts)
        # flat map the contexts and eliminate duplicate entries
        contexts = list(set(itertools.chain.from_iterable(contexts)))

        # add contexts required by the verification methods
        did_doc_builder.context.extend(contexts)
        did_doc_builder.verification_method.methods.extend(verification_methods)

        # reference the keys in the other sections
        all_key_references = _build_key_references(did, keys_with_indices)
        did_doc_builder.authentication.methods.extend(all_key_references)
        did_doc_builder.assertion_method.methods.extend(all_key_references)

        # add routing information
        routing_keys, endpoint = await self._retrieve_routing_information()
        did_doc_builder.service.add_didcomm(
            endpoint,
            recipient_keys=[did_doc_builder.verification_method.methods[0]],
            routing_keys=[
                DIDKey.from_public_key_b58(key, key_type=ED25519).did
                for key in routing_keys
            ]
            if routing_keys is not None
            else [],
        )

        return did_doc_builder.build()

    async def rotate_key(self, did: str):
        # Safe keep the old key
        did_info, signing_key = await self._get_did_and_signing_key(did)
        await self.__storage_strategy.store_old_key(did, signing_key)

        # Rotate key in wallet
        await self.__wallet.rotate_did_keypair_start(did)
        await self.__wallet.rotate_did_keypair_apply(did)

        # Return new DIDDoc
        return await self.get_diddoc(did)

    async def _get_did_and_signing_key(self, did) -> Tuple[DIDInfo, bytes]:
        try:
            did_info = await self.__wallet.get_local_did(did.replace("did:sov:", ""))
            signing_key = base58.b58decode(did_info.verkey)

            return did_info, signing_key
        except WalletNotFoundError:
            raise UnknownDIDException()

    async def _retrieve_routing_information(self) -> Tuple[List[str], str]:
        route_manager = self.__profile.inject(RouteManager)

        routing_keys, my_endpoint = await route_manager.routing_info(
            self.__profile,
            None,
        )
        return routing_keys, my_endpoint or cast(
            str, self.__profile.settings.get("default_endpoint")
        )


def _build_key_references(
    did: str, keys_with_indices: Iterable[Tuple[int, bytes]]
) -> List[DIDUrl]:
    return [DIDUrl(f"{did}#key-{index}") for index, _ in keys_with_indices]


def _get_default_context():
    return [context for context in DIDDocumentBuilder.DEFAULT_CONTEXT]
