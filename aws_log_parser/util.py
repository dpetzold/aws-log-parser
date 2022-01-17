import socket
import time

from functools import cache
from itertools import islice


def batcher(iterable, batch_size):
    iterator = iter(iterable)
    while batch := list(islice(iterator, batch_size)):
        yield batch


def time_ms():
    return (time.time_ns() + 500000) // 1000000


@cache
def gethostbyname(hostname):
    return socket.gethostbyname(hostname)
