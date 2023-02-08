from aiohttp import web

from .register_route import register_route
from .get_diddoc import fetch_diddoc
from .rotate_key import rotate_key

from .openapi_config import SPEC_URI, OPENAPI_TAG


async def register(app: web.Application):
    """Register routes."""
    app.add_routes(
        [
            web.get("/didweb/diddoc", fetch_diddoc),
            web.put("/didweb/rotate", rotate_key),
            web.put("/routing/register_route", register_route),
        ]
    )


def post_process_routes(app: web.Application):
    """Amend swagger API."""
    # Add top-level tags description
    if "tags" not in app._state["swagger_dict"]:
        app._state["swagger_dict"]["tags"] = []

    app._state["swagger_dict"]["tags"].append(
        {
            "name": OPENAPI_TAG,
            "description": "did:web management",
            "externalDocs": {"description": "Specification", "url": SPEC_URI},
        }
    )


__all__ = ["register", "post_process_routes"]
