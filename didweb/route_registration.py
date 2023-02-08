from aries_cloudagent.protocols.routing.v1_0.manager import RoutingManager
from aries_cloudagent.protocols.routing.v1_0.models.route_record import RouteRecord
from aries_cloudagent.wallet.base import BaseWallet


class RouteRegistrar:
    """No route ? No worries."""

    def __init__(self, wallet: BaseWallet, routing_manager: RoutingManager):
        self.__wallet = wallet
        self.__routing_manager = routing_manager

    async def register_route(self, did: str, wallet_id: str) -> RouteRecord:
        """
        Register a route given a did and a recipient wallet
        :param did: DID on the receiving end of the route
        :param wallet_id: wallet on the receiving end of the route
        :return:
        """
        did_record = await self.__wallet.get_local_did(did)
        return await self.__routing_manager.create_route_record(
            recipient_key=did_record.verkey, internal_wallet_id=wallet_id
        )
