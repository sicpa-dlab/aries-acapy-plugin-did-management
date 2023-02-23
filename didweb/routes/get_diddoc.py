from aiohttp import web
from aiohttp_apispec import querystring_schema, response_schema
from aiohttp_apispec.decorators import docs
from aries_cloudagent.admin.request_context import AdminRequestContext
from aries_cloudagent.storage.base import BaseStorage
from aries_cloudagent.wallet.base import BaseWallet

from ..didweb_manager import DIDWebManager
from .openapi_config import OPENAPI_TAG
from .schemas import GetDIDDocSchema, DIDDocSchema
from ..retention import RecallStrategyConfig


@docs(tags=[OPENAPI_TAG], summary="Gets DIDDoc for specified did:web")
@querystring_schema(GetDIDDocSchema())
@response_schema(DIDDocSchema())
async def fetch_diddoc(request: web.Request):
    did = request.query.get("did")
    if not did:
        raise web.HTTPBadRequest(reason="Request query must include DID")
    number_of_keys = int(request.query.get("number_of_keys", "1"))

    context: AdminRequestContext = request["context"]

    async with context.profile.session() as session:
        retention_strategy_config = (
            RecallStrategyConfig(number_of_keys - 1) if number_of_keys >= 1 else None
        )

        manager = DIDWebManager(
            context.profile,
            session.inject(BaseWallet),
            session.inject(BaseStorage),
            retention_strategy_config,
        )

        diddoc = await manager.get_diddoc(did)

    return web.json_response(text=diddoc.to_json())
