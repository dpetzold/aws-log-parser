import functools
import logging
import socket

import whois

logger = logging.getLogger(__name__)


@functools.lru_cache(maxsize=128)
def gethostbyname(hostname: str) -> str:
    return socket.gethostbyname(hostname)


@functools.lru_cache(maxsize=16384)
def query_radb(ip_address: str) -> dict:
    try:
        query = whois.NICClient().whois(
            ip_address,
            gethostbyname("whois.radb.net"),
            0,
        )
    except (
        socket.gaierror,
        socket.herror,
        socket.timeout,
        ConnectionResetError,
    ) as exc:
        logger.error(f"{ip_address} lookup failed: {str(exc)}")
        return {}

    d = {}
    for line in query.split("\n"):
        if line == "":
            break
        if ":" not in line:
            continue
        s = line.split(":", 1)
        d[s[0].strip()] = s[1].strip()
    return d
