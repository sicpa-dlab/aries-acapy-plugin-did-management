from aiohttp import web

from .mark_did_public import set_public_did
from .register_route import register_route
from .get_diddoc import fetch_diddoc
from .rotate_key import rotate_key


async def register(app: web.Application):
    """Register routes."""
    app.add_routes(
        [
            web.get("/wallet/{did}/diddoc", fetch_diddoc, allow_head=False),
            web.put("/wallet/{did}/rotate-keys", rotate_key),
            web.put("/wallet/{did}/routing/register-route", register_route),
            web.put("/wallet/{did}/mark-public", set_public_did),
        ]
    )


__all__ = ["register"]
