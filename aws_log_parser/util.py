import socket

from functools import cache
from itertools import islice


def batcher(iterable, batch_size):
    iterator = iter(iterable)
    while batch := list(islice(iterator, batch_size)):
        yield batch


@cache
def gethostbyname(hostname):
    return socket.gethostbyname(hostname)
