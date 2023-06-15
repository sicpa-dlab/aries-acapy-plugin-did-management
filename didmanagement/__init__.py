import logging

from aries_cloudagent.config.injection_context import InjectionContext
from aries_cloudagent.wallet.default_verification_key_strategy import BaseVerificationKeyStrategy

from didmanagement.verification_methods import DidManagerVerificationKeyStrategy

logger = logging.getLogger(__name__)


async def setup(context: InjectionContext):
    """Load DidManagerVerificationKeyStrategy plugin."""
    logger.info("Loading DidManagerVerificationKeyStrategy in the context")
    context.injector.bind_instance(BaseVerificationKeyStrategy, DidManagerVerificationKeyStrategy())
