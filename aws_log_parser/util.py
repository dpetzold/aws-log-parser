import functools
import logging
import socket

import whois

logger = logging.getLogger(__name__)


@functools.lru_cache(maxsize=16384)
def gethostbyaddr(source_ip) -> str:
    socket.setdefaulttimeout(.500)
    try:
        return socket.gethostbyaddr(source_ip)[0]
    except (socket.herror, socket.gaierror) as exc:
        logger.error('Unable to resolve {} {}'.format(source_ip, str(exc)))
        return None


@functools.lru_cache(maxsize=1)
def gethostbyname(hostname: str) -> str:
    return socket.gethostbyname(hostname)


@functools.lru_cache(maxsize=16384)
def query_radb(ip_address: str) -> dict:
    try:
        query = whois.NICClient().whois(
            ip_address,
            gethostbyname('whois.radb.net'),
            0,
        )
    except (
        socket.gaierror,
        socket.herror,
        socket.timeout,
        ConnectionResetError,
    ) as exc:
        logger.error(f'{ip_address} lookup failed: {str(exc)}')
        return {}

    d = {}
    for line in query.split('\n'):
        if ':' not in line:
            continue
        s = line.split(':', 1)
        d[s[0].strip()] = s[1].strip()
    return d
