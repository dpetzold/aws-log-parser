from itertools import islice
import gzip


def yield_file(fileobj, file_name):

    if file_name.endswith(".gz"):
        with gzip.GzipFile(fileobj=fileobj, mode="r") as _gz:
            yield from [line for line in _gz.read().decode("utf-8").splitlines()]
    else:
        yield from [line.decode("utf-8") for line in fileobj.iter_lines()]


def batcher(iterable, batch_size):
    iterator = iter(iterable)
    while batch := list(islice(iterator, batch_size)):
        yield batch
