from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
import io
import gzip
import typing


@dataclass
class FileIterator:
    path: typing.Optional[Path] = None
    fileobj: typing.Optional[io.IOBase] = None
    gzipped: bool = False

    def yield_gzipped(self, fh):
        yield from [line for line in fh.read().decode("utf-8").splitlines()]

    def yield_plain(self, fh):
        yield from [line.decode("utf-8") for line in fh]

    @contextmanager
    def open_path(self):
        assert self.path
        fh = self.path.open("rb")
        try:
            yield fh
        finally:
            fh.close()

    @contextmanager
    def open_gzip(self):
        if self.fileobj:
            yield gzip.GzipFile(fileobj=self.fileobj)
        else:
            with self.open_path() as fh:
                yield gzip.GzipFile(fileobj=fh)

    def __iter__(self):
        yield_func = self.yield_gzipped if self.gzipped else self.yield_plain
        open_func = self.open_gzip if self.gzipped else self.open_path

        if not self.gzipped and self.fileobj:
            yield from yield_func(self.fileobj)
        else:
            with open_func() as fh:
                yield from yield_func(fh)
