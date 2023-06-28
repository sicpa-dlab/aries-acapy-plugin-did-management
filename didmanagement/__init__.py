import logging

from aries_cloudagent.config.injection_context import InjectionContext
from aries_cloudagent.wallet.default_verification_key_strategy import BaseVerificationKeyStrategy

from didmanagement.verification_methods import LatestVerificationKeyStrategy

logger = logging.getLogger(__name__)


async def setup(context: InjectionContext):
    """Load LatestVerificationKeyStrategy plugin."""
    logger.info("Loading LatestVerificationKeyStrategy in the context")
    context.injector.bind_instance(BaseVerificationKeyStrategy, LatestVerificationKeyStrategy())
