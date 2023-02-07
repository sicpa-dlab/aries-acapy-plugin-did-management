import base58
from pydid.verification_method import JsonWebKey2020, Ed25519VerificationKey2018

Did = str


def json_web_key_2020(did_value: Did, key_index: int, key: bytes) -> JsonWebKey2020:
    return JsonWebKey2020(
        id=_verification_method_id(did_value, key_index),
        type=JsonWebKey2020.__name__,
        controller=did_value,
        public_key_jwk={
            "kty": "OKP",
            # TODO: remove hard-coding if we want to support more key types
            "crv": "Ed25519",
            "x": key,
        },
    )


def ed25519_verification_key_2018(
    did_value: Did, key_index: int, key: bytes
) -> Ed25519VerificationKey2018:
    return Ed25519VerificationKey2018(
        id=_verification_method_id(did_value, key_index),
        type=Ed25519VerificationKey2018.__name__,
        controller=did_value,
        public_key_base58=base58.b58encode(key),
    )


def _verification_method_id(did_value: Did, key_index: int) -> str:
    return f"{did_value}#key-{key_index}"
