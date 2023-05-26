from aiohttp import web
from aiohttp_apispec import response_schema, match_info_schema
from aiohttp_apispec.decorators import docs

from aries_cloudagent.admin.request_context import AdminRequestContext
from aries_cloudagent.storage.base import BaseStorage
from aries_cloudagent.wallet.base import BaseWallet

from ..didweb_manager import DIDWebManager
from .openapi_config import OPENAPI_TAG
from .schemas import DIDDocSchema, DIDSchema


@docs(tags=[OPENAPI_TAG], summary="Rotate keys for specified did, returns new DIDDoc")
@match_info_schema(DIDSchema())
@response_schema(DIDDocSchema())
async def rotate_key(request: web.Request):
    did = request.match_info.get("did")
    if not did:
        raise web.HTTPBadRequest(reason="Request query must include DID")

    context: AdminRequestContext = request["context"]

    async with context.profile.transaction() as transaction:
        manager = DIDWebManager(
            context.profile,
            transaction.inject(BaseWallet),
            transaction.inject(BaseStorage),
        )

        new_diddoc = await manager.rotate_key(did)
        await transaction.commit()

    return web.Response(text=new_diddoc.to_json())
