import functools
import logging
import socket

logger = logging.getLogger(__name__)


@functools.lru_cache(maxsize=16384)
def resolve_ip(source_ip):
    socket.setdefaulttimeout(.500)
    try:
        return socket.gethostbyaddr(source_ip)[0]
    except (socket.herror, socket.gaierror) as exc:
        logger.error('Unable to resolve {} {}'.format(source_ip, str(exc)))
        return None
