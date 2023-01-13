import re

from aries_cloudagent.messaging.models.openapi import OpenAPISchema
from marshmallow import fields
from marshmallow.validate import Regexp


class WebDID(Regexp):
    """Validate value against web DID."""

    EXAMPLE = "did:web:mydoma.in:some:weird:path"
    PATTERN = re.compile(rf"^(did:web:)?[a-z]+\.[a-z]+(%3A[0-9]+)*(:[a-z]+)*$")

    def __init__(self):
        """Initializer."""

        super().__init__(
            WebDID.PATTERN,
            error="Value {input} is not an indy decentralized identifier (DID)",
        )


WEB_DID = {"validate": WebDID(), "example": WebDID.EXAMPLE}


class DIDWebSchema(OpenAPISchema):
    """
    """

    did = fields.Str(
        required=True,
        **WEB_DID
    )

class DIDQueryStringSchema(OpenAPISchema):
    """Parameters and validators for set public DID request query string."""

    did = fields.Str(description="DID of interest", required=True, **WEB_DID)


class DIDWebDIDDocSchema(OpenAPISchema):
    """
    """

    very = fields.Str(required=True, default="nice")
