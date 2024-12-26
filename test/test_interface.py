import pytest
import datetime

from dataclasses import dataclass
from dateutil.tz import tzutc
from pathlib import Path

from aws_log_parser import (
    AwsLogParser,
    LogType,
)


from aws_log_parser.aws.s3 import S3Service


@dataclass
class MockPaginator:
    gzipped: bool = False

    def paginate(self, **_):
        suffix = ".gz" if self.gzipped else ""
        yield {
            "Contents": [
                {
                    "Key": f"cloudfront-multiple.log{suffix}",
                    "LastModified": datetime.datetime(
                        2021, 11, 28, 3, 31, 56, tzinfo=tzutc()
                    ),
                    "ETag": '"37c13f9a66a79c2b474356adaf5da1d0"',
                    "Size": 2844,
                    "StorageClass": "STANDARD",
                }
            ],
        }


@dataclass
class MockStreamingFile:
    filename: str

    def iter_lines(self):
        return open(self.filename, "rb").read()


@dataclass
class MockS3Client:
    gzipped: bool = False

    def get_paginator(self, *_):
        return MockPaginator(self.gzipped)

    def get_object(self, **_):
        suffix = ".gz" if self.gzipped else ""
        return {"Body": MockStreamingFile(f"test/data/cloudfront-multiple.log{suffix}")}


@pytest.fixture
def cloudfront_parser():
    return AwsLogParser(
        log_type=LogType.CloudFront,
    )


def test_parse_file(cloudfront_parser):
    entries = cloudfront_parser.read_file("test/data/cloudfront-multiple.log")
    assert len(list(entries)) == 6


def test_parse_files():
    parser = AwsLogParser(
        log_type=LogType.CloudFront,
        verbose=True,
        regex_filter=r"^cloudfront",
    )
    entries = parser.read_files("test/data")
    assert len(list(entries)) == 6


def test_parse_s3(monkeypatch, cloudfront_parser, gzipped=False):
    monkeypatch.setattr(S3Service, "client", MockS3Client(gzipped=gzipped))
    suffix = ".gz" if gzipped else ""

    entries = cloudfront_parser.read_s3(
        "bucket",
        "key",
        endswith=suffix,
    )
    assert len(list(entries)) == 6


def test_parse_s3_gzipped(monkeypatch, cloudfront_parser):
    gzipped = True
    monkeypatch.setattr(S3Service, "client", MockS3Client(gzipped=gzipped))
    suffix = ".gz" if gzipped else ""

    entries = cloudfront_parser.read_s3(
        "bucket",
        "key",
        endswith=suffix,
    )
    assert len(list(entries)) == 6


def test_parse_url_s3(monkeypatch, cloudfront_parser):
    monkeypatch.setattr(S3Service, "client", MockS3Client())
    entries = cloudfront_parser.read_url(
        "s3://aws-logs-test-data/cloudfront-multiple.log"
    )
    assert len(list(entries)) == 6


def test_parse_url_file(cloudfront_parser):
    entries = cloudfront_parser.read_url(
        f"file://{Path(__file__).parent}/data/cloudfront-multiple.log"
    )
    assert len(list(entries)) == 6


def test_parse_url_gopher(cloudfront_parser):
    with pytest.raises(ValueError):
        list(cloudfront_parser.read_url("gopher://"))
