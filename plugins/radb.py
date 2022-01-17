import logging
import socket

from dataclasses import dataclass

import whois

from aws_log_parser.plugin import AwsLogParserPlugin
from aws_log_parser.util import gethostbyname

logger = logging.getLogger(__name__)


@dataclass
class RadbPlugin(AwsLogParserPlugin):
    """
    Get the public network name from RADB.
    """

    consumed_attr: str = "client_ip"
    produced_attr: str = "network"

    def parse_response(self, response):
        d = {}
        for line in response.split("\n"):
            if line == "":
                break
            if ":" not in line:
                continue
            s = line.split(":", 1)
            d[s[0].strip()] = s[1].strip()
        return d

    def query(self, ip_address):
        try:
            response = whois.NICClient().whois(
                ip_address,
                gethostbyname("whois.radb.net"),
                0,
            )
        except (
            socket.gaierror,
            socket.herror,
            socket.timeout,
            ConnectionResetError,
        ):
            logger.debug(f"{ip_address} lookup failed", exc_info=True)
        else:
            return self.parse_response(response).get("descr")

    def augment(self, log_entries):

        print(f"{self.produced_attr} augmenting ({len(self._results)})")

        for i, log_entry in enumerate(log_entries):
            setattr(
                log_entry, self.produced_attr, self._results.get(log_entry.client_ip)
            )
            yield log_entry

        print(f"{self.produced_attr} augmenting completed ({i})")
