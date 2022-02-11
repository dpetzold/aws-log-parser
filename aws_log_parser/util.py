import gzip
import socket
import time

from functools import cache
from itertools import islice


def yield_file(path):
    with open(path) as log_data:
        yield from log_data.readlines()


def yield_gzip(path):
    with gzip.open(path, "rt") as f:
        yield from f.readlines()


def batcher(iterable, batch_size):
    iterator = iter(iterable)
    while batch := list(islice(iterator, batch_size)):
        yield batch


def time_ms():
    return (time.time_ns() + 500000) // 1000000


@cache
def gethostbyname(hostname):
    return socket.gethostbyname(hostname)
