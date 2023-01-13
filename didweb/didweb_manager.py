import base64
from typing import Mapping, Iterable, Tuple, Collection, List

import base58
from aries_cloudagent.storage.base import BaseStorage
from aries_cloudagent.storage.record import StorageRecord
from aries_cloudagent.wallet.base import BaseWallet
from aries_cloudagent.wallet.did_info import DIDInfo

from pydid import DIDDocumentBuilder, DIDUrl
from pydid.verification_method import JsonWebKey2020, VerificationMethod

PREVIOUS_PUBLIC_KEY_RECORD_TYPE = "PREVIOUS_PUBLIC_KEY"


class UnknownDIDException(Exception):
    """When trying to operate on an unknown DID."""


class DIDWebManager:
    def __init__(self, wallet: BaseWallet, storage: BaseStorage):
        self.__wallet = wallet
        self.__storage = storage

    async def get_diddoc(self, did: str):
        # fetch did with current key
        did_info, signing_key_b64 = await self._get_did_and_signing_key(did)
        if not did_info:
            raise UnknownDIDException()

        # Also retrieve n previous keys
        previous_keys = await self._previous_keys(did)

        # Build diddoc
        did_doc_builder = DIDDocumentBuilder(did, controller=[did])
        keys_with_indices = _keys_and_indices(previous_keys, signing_key_b64)

        verification_methods = _build_verification_methods(did, keys_with_indices)
        did_doc_builder.verification_method.methods.extend(verification_methods)

        # reference the keys in the authentication and assertion
        all_key_references = _build_key_references(did, keys_with_indices)
        did_doc_builder.authentication.methods.extend(all_key_references)
        did_doc_builder.assertion_method.methods.extend(all_key_references)

        return did_doc_builder.build()

    async def rotate_key(self, did: str):
        did_info, signing_key_b64 = await self._get_did_and_signing_key(did)

        previous_keys = await self._previous_keys(did)
        index = _current_index(previous_keys)

        # Store current key
        # record: (type, value, tags, id)
        current_key_record = StorageRecord(
            PREVIOUS_PUBLIC_KEY_RECORD_TYPE,
            signing_key_b64,
            {"did": did, "index": str(index)},
            f"{did_info.did}{index}"
        )
        await self.__storage.add_record(current_key_record)

        # Rotate key in wallet
        await self.__wallet.rotate_did_keypair_start(did)
        await self.__wallet.rotate_did_keypair_apply(did)

        # Return new DIDDoc
        return await self.get_diddoc(did)

    async def _get_did_and_signing_key(self, did) -> Tuple[DIDInfo, bytes]:
        did_info = await self.__wallet.get_local_did(did)
        signing_key_b64 = base64.b64encode(base58.b58decode(did_info.verkey))

        return did_info, signing_key_b64

    async def _previous_keys(self, did) -> Mapping[int, bytes]:
        previous_keys = await self.__storage.find_all_records(PREVIOUS_PUBLIC_KEY_RECORD_TYPE, {"did": did})
        return {int(key.tags.get("index")): key.value for key in previous_keys}


def _keys_and_indices(previous_keys: Mapping[int, bytes], current_key: bytes) -> Iterable[Tuple[int, bytes]]:
    keys = [(index, verkey) for index, verkey in previous_keys.items()]
    keys.append((_current_index(previous_keys.keys()), current_key))

    return keys


def _current_index(indices: Collection[int]) -> int:
    return max(indices) + 1 if len(indices) > 0 else 1


def _build_verification_methods(did: str, keys_with_indices: Iterable[Tuple[int, bytes]]) -> List[VerificationMethod]:
    return [
        JsonWebKey2020(
            id=f"{did}#key-{index}",
            type="JsonWebKey2020",
            controller=did,
            public_key_jwk={
                "kty": "OKP",
                "crv": "Ed25519",  # TODO: remove hard-coding if we want to support more key types
                "x": signing_key
            }
        )
        for index, signing_key
        in keys_with_indices
    ]


def _build_key_references(did: str, keys_with_indices: Iterable[Tuple[int, bytes]]) -> List[DIDUrl]:
    return [
        DIDUrl(f"{did}#key-{index}")
        for index, _
        in keys_with_indices
    ]
