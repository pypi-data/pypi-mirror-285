import logging
from datetime import datetime

from pythonosc import osc_bundle_builder, osc_message_builder, udp_client

logger = logging.getLogger(__name__)


class OscClient:
    def __init__(self, address: str, port: int) -> None:
        self.__client = udp_client.SimpleUDPClient(address, port)

    def send(self, address: str, args: dict, timestamp: float) -> None:
        bundle = osc_bundle_builder.OscBundleBuilder(timestamp)  # type: ignore
        msg = osc_message_builder.OscMessageBuilder(address=address)
        for k, v in args.items():
            msg.add_arg(k)
            msg.add_arg(v)
        bundle.add_content(msg.build())  # type: ignore
        self.__client.send(bundle.build())


class SuperDirtClient:
    ADDRESS: str = "/dirt/play"

    def __init__(
        self, address: str = "127.0.0.1", port: int = 57120, delay: float = 1.0
    ) -> None:
        self.__client = OscClient(address, port)
        self.__delay = delay

    def send(self, event: dict, timestamp: datetime, dryrun: bool = False) -> None:
        if dryrun:
            return
        logger.debug(event)
        self.__client.send(
            address=self.ADDRESS,
            args=event,
            timestamp=timestamp.timestamp() + self.__delay,
        )
