from aiohttp import web
from aiohttp_apispec import docs, match_info_schema, response_schema
from aries_cloudagent.admin.request_context import AdminRequestContext
from aries_cloudagent.wallet.base import BaseWallet
from aries_cloudagent.wallet.did_posture import DIDPosture
from aries_cloudagent.wallet.routes import DIDResultSchema

from .openapi_config import OPENAPI_TAG
from didweb.routes.schemas import DIDSchema


@docs(
    tags=[OPENAPI_TAG],
    summary="Set public DID of the wallet."
    "This is limited to the wallet, no ledger interaction.",
)
@match_info_schema(DIDSchema())
@response_schema(DIDResultSchema, 200, description="The updated did.")
async def set_public_did(request: web.Request):
    did = request.match_info.get("did")
    if not did:
        raise web.HTTPBadRequest(reason="Request query must include DID")

    context: AdminRequestContext = request["context"]

    async with context.profile.transaction() as transaction:
        did_info = await transaction.inject(BaseWallet).set_public_did(did)
        await transaction.commit()

    return web.json_response(
        data={
            "did": did_info.did,
            "verkey": did_info.verkey,
            "posture": DIDPosture.get(did_info.metadata).moniker,
            "key_type": did_info.key_type.key_type,
            "method": did_info.method.method_name,
        }
    )
