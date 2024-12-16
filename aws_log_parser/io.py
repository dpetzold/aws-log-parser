from dataclasses import dataclass
import io


@dataclass
class FileIterator:
    fileobj: io.IOBase
    gzipped: bool = False

    def yield_gzipped(self, fh):
        yield from [line for line in fh.read().decode("utf-8").splitlines()]

    def yield_plain(self, fh):
        yield from [line.decode("utf-8") for line in fh]

    def __iter__(self):
        yield_func = self.yield_gzipped if self.gzipped else self.yield_plain
        yield from yield_func(self.fileobj)
