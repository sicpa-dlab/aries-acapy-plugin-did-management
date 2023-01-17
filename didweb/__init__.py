from aries_cloudagent.config.injection_context import InjectionContext
from aries_cloudagent.wallet.did_method import DIDMethod, DIDMethods, HolderDefinedDid
from aries_cloudagent.wallet.key_type import ED25519

WEB = DIDMethod(
    name="web",
    key_types=[ED25519],
    rotation=True,
    holder_defined_did=HolderDefinedDid.REQUIRED,
)


async def setup(context: InjectionContext):
    methods = context.inject(DIDMethods)
    methods.register(WEB)
