import logging
import socket
import time
import typing

import concurrent.futures

from dataclasses import dataclass, field

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
    hostnames: typing.Dict[str, str] = field(default_factory=dict)

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

    def _lookup(self, client_ips):

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            query_future = {
                executor.submit(self._query, client_ip): client_ip
                for client_ip in client_ips
            }

            for future in concurrent.futures.as_completed(query_future):
                client_ip = query_future[future]
                try:
                    hostname = future.result()
                except Exception:
                    logger.error(f"{client_ip} generated an exception", exc_info=True)
                else:
                    if client_ip and hostname:
                        self.hostnames[client_ip] = hostname

    def augment(self, log_entries):

        client_ips = {log_entry.client_ip for log_entry in log_entries}

        unknown = client_ips - self.hostnames.keys()

        print(
            " ".join(
                [
                    f"unknown={len(unknown):,}",
                    f"found={len(client_ips)-len(unknown)}",
                    f"total={len(client_ips):,}",
                ]
            )
        )

        start = time.time()
        self._lookup(unknown)
        spent = time.time() - start
        print(f"{spent:.2f}s avg={(spent/len(unknown))*100:.2f}")

        for log_entry in log_entries:
            setattr(log_entry, self.attr_name, self.hostnames.get(log_entry.client_ip))
            yield log_entry
