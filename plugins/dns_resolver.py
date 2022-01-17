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

    attr_name: str = "hostname"
    socket_timeout: float = 0.5
    requests: int = 0

    def _query(self, ip_address):
        self.requests += 1
        socket.setdefaulttimeout(self.socket_timeout)
        try:
            hostname = socket.gethostbyaddr(ip_address)[0]
        except (socket.herror, socket.gaierror):
            logger.debug(f"Unable to resolve {ip_address}", exc_info=True)
        else:
            return hostname

    def query(self, ip_addresses):
        for ip_address in ip_addresses:
            self._query(ip_address)

    def augment(self, log_entries):

        client_ips = {log_entry.client_ip for log_entry in log_entries}

        hostnames = self.lookup(client_ips)

        for log_entry in log_entries:
            setattr(log_entry, self.attr_name, hostnames.get(log_entry.client_ip))
            yield log_entry
