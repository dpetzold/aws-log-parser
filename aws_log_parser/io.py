from dataclasses import dataclass
import io


@dataclass
class FileIterator:
    fileobj: io.IOBase
    gzipped: bool = False

    def yield_gzipped(self, fh):
        yield from [line for line in fh.read().decode("utf-8").splitlines()]

    def yield_plain(self, fh):
        yield from [line.decode("utf-8") for line in fh.iter_lines()]

    def __iter__(self):
        return self

    def __next__(self):
        if self.gzipped:
            yield from self.yield_gzipped(self.fileobj)
        else:
            yield from self.yield_plain(self.fileobj)
