from aiohttp import web
from aiohttp_apispec import querystring_schema
from aiohttp_apispec.decorators import docs
from aries_cloudagent.admin.request_context import AdminRequestContext
from aries_cloudagent.protocols.coordinate_mediation.v1_0.route_manager import (
    RouteManager,
)
from aries_cloudagent.wallet.base import BaseWallet

from ..route_registration import RouteRegistrar
from .openapi_config import OPENAPI_TAG
from .schemas import DIDSchema


@docs(
    tags=[OPENAPI_TAG],
    summary="Registers a route for a given DID within a multi-tenanted agent.",
    responses={201: {"description": "Route registered."}},
)
@querystring_schema(DIDSchema())
async def register_route(request: web.Request):
    did = request.query.get("did")
    if not did:
        raise web.HTTPBadRequest(reason="Request query must include DID")

    context: AdminRequestContext = request["context"]

    async with context.profile.transaction() as transaction:
        route_registrar = RouteRegistrar(
            context.profile,
            transaction.inject(BaseWallet),
            transaction.inject(RouteManager),
        )
        await route_registrar.register_route(did)
        await transaction.commit()

    return web.Response(status=201)
