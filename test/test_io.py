from pathlib import Path
from aws_log_parser.io import FileIterator


def test_fileiterator_plain():

    file_iterator = FileIterator(Path("test/data/cloudfront-multiple.log").open("rb"))
    assert len(list(file_iterator)) == 8


def test_fileiterator_gzipped():

    file_iterator = FileIterator(
        Path("test/data/loadbalancer_http2_entry.csv.gz").open("rb")
    )
    assert len(list(file_iterator)) == 8
