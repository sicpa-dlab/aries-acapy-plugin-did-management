import base64
import logging
from typing import List, Tuple, Optional

import base58
from aries_cloudagent.core.profile import Profile
from aries_cloudagent.storage.base import BaseStorage
from aries_cloudagent.wallet.default_verification_key_strategy import BaseVerificationKeyStrategy
from aries_cloudagent.wallet.key_type import KeyType
from pydid.verification_method import JsonWebKey2020, Ed25519VerificationKey2018

from didmanagement.retention import StorageBackendStorageStrategy

Did = str

logger = logging.getLogger(__name__)


def json_web_key_2020(did_value: Did, key_index: int, key: bytes) -> Tuple[JsonWebKey2020, List[str]]:
    return JsonWebKey2020(
        id=_verification_method_id(did_value, key_index),
        type=JsonWebKey2020.__name__,
        controller=did_value,
        public_key_jwk={
            "kty": "OKP",
            # TODO: remove hard-coding if we want to support more key types
            "crv": "Ed25519",
            "x": base64.b64encode(key),
        },
    ), ["https://w3id.org/security/suite/jws-2020/v1"]


def ed25519_verification_key_2018(
    did_value: Did, key_index: int, key: bytes
) -> Tuple[Ed25519VerificationKey2018, List[str]]:
    return Ed25519VerificationKey2018(
        id=_verification_method_id(did_value, key_index),
        type=Ed25519VerificationKey2018.__name__,
        controller=did_value,
        public_key_base58=base58.b58encode(key),
    ), ["https://w3id.org/security/suites/ed25519-2018/v1"]


class LatestVerificationKeyStrategy(BaseVerificationKeyStrategy):
    async def get_verification_method_id_for_did(self, did: str,
                                                 profile: Optional[Profile],
                                                 allowed_verification_method_types: Optional[List[KeyType]] = None,
                                                 proof_purpose: Optional[str] = None) -> Optional[str]:

        async with profile.session() as session:
            storage = session.inject(BaseStorage)
            storage_strategy = StorageBackendStorageStrategy(storage)
            curr_idx = await storage_strategy.current_index(did)
            return _verification_method_id(did, curr_idx)


def _verification_method_id(did_value: Did, key_index: int) -> str:
    return f"{did_value}#key-{key_index}"
