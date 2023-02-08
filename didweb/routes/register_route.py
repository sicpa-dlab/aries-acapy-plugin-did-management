from aiohttp import web
from aiohttp_apispec import querystring_schema, response_schema
from aiohttp_apispec.decorators import docs
from aries_cloudagent.admin.request_context import AdminRequestContext
from aries_cloudagent.protocols.routing.v1_0.manager import RoutingManager
from aries_cloudagent.protocols.routing.v1_0.models.route_record import RouteRecordSchema
from aries_cloudagent.wallet.base import BaseWallet

from ..route_registration import RouteRegistrar
from .openapi_config import OPENAPI_TAG
from .schemas import DIDSchema


@docs(
    tags=[OPENAPI_TAG],
    summary="Registers a route for a given DID within a multi-tenanted agent.",
)
@querystring_schema(DIDSchema())
@response_schema(RouteRecordSchema())
async def register_route(request: web.Request):
    did = request.query.get("did")
    if not did:
        raise web.HTTPBadRequest(reason="Request query must include DID")

    context: AdminRequestContext = request["context"]

    print(context.profile.settings)
    try:
        wallet_id = context.profile.settings["wallet.id"]
    except KeyError:
        return web.Response(
            status=404,
            text="Registering routes is not necessary for single-tenant agents.",
        )

    async with context.profile.transaction() as transaction:
        route_registrar = RouteRegistrar(
            transaction.inject(BaseWallet), RoutingManager(context.profile)
        )
        route_record = await route_registrar.register_route(did, wallet_id)

        await transaction.commit()

    return web.Response(text=RouteRecordSchema().dumps(route_record))
