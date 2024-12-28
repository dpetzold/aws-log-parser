from io import BytesIO
from pathlib import Path
from aws_log_parser.io import FileIterator


def test_fileiterator_plain():
    file_iterator = FileIterator(Path("test/data/cloudfront-multiple.log"))
    assert len(list(file_iterator)) == 8


def test_fileiterator_gzipped_path():
    file_iterator = FileIterator(
        path=Path("test/data/loadbalancer_http2_entry.csv.gz"),
        gzipped=True,
    )
    assert len(list(file_iterator)) == 1


def test_fileiterator_gzipped_fileobj():
    file_iterator = FileIterator(
        fileobj=BytesIO(
            Path("test/data/loadbalancer_http2_entry.csv.gz").open("rb").read()
        ),
        gzipped=True,
    )
    assert len(list(file_iterator)) == 1
