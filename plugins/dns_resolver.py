import logging
import socket

from dataclasses import dataclass

from aws_log_parser.plugin import AwsLogParserPlugin

logger = logging.getLogger(__name__)


@dataclass
class IpResolverPlugin(AwsLogParserPlugin):
    """
    Resolve the hostname from the client ip address.
    """

    consumed_attr: str = "client_ip"
    produced_attr: str = "hostname"
    socket_timeout: float = 0.5
    requests: int = 0

    def query(self, ip_address):
        self.requests += 1
        # socket.setdefaulttimeout(self.socket_timeout)
        try:
            hostname = socket.gethostbyaddr(ip_address)[0]
        except (socket.herror, socket.gaierror):
            logger.debug(f"Unable to resolve {ip_address}", exc_info=True)
            return {ip_address: None}
        else:
            return {ip_address: hostname}
