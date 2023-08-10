import re

from marshmallow import fields, INCLUDE, Schema
from marshmallow.validate import Regexp

from aries_cloudagent.messaging.models.openapi import OpenAPISchema
from aries_cloudagent.messaging.valid import GENERIC_DID_VALIDATE


class WebDID(Regexp):
    """Validate value against web DID."""

    EXAMPLE = "did:web:mydoma.in:some:weird:path"
    PATTERN = re.compile(r"^(did:web:)?[a-z]+\.[a-z]+(%3A[0-9]+)*(:[a-z]+)*$")

    def __init__(self):
        """Initializer."""

        super().__init__(
            WebDID.PATTERN,
            error="Value {input} is not an indy decentralized identifier (DID)",
        )


WEB_DID = {"validate": WebDID(), "example": WebDID.EXAMPLE}


class KeyRetentionConfigSchema(OpenAPISchema):
    """ """

    number_of_keys = fields.Int(required=True)


class DIDSchema(OpenAPISchema):
    """ """

    did = fields.Str(required=True, validate=GENERIC_DID_VALIDATE)


class GetDIDDocSchema(OpenAPISchema):
    number_of_keys = fields.Int(required=False)


class DIDQueryStringSchema(OpenAPISchema):
    """Parameters and validators for set public DID request query string."""

    did = fields.Str(description="DID of interest", required=True, validate=GENERIC_DID_VALIDATE)


class DIDDocSchema(Schema):
    class Meta:
        unknown = INCLUDE
