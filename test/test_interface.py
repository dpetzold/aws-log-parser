import pytest
import datetime
import typing

from dataclasses import dataclass
from dateutil.tz import tzutc

from aws_log_parser import (
    AwsLogParser,
    LogType,
)


from aws_log_parser.aws.s3 import S3Service


class MockPaginator:
    def paginate(self, **kwargs):
        yield {
            "Contents": [
                {
                    "Key": "cloudfront-multiple.log",
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
    contents: typing.BinaryIO

    def iter_lines(self):
        return self.contents.readlines()


class MockS3Client:
    def get_paginator(self, *args):
        return MockPaginator()

    def get_object(self, **kwargs):
        return {
            "Body": MockStreamingFile(open("test/data/cloudfront-multiple.log", "rb"))
        }


@pytest.fixture
def cloudfront_parser():
    return AwsLogParser(
        log_type=LogType.CloudFront,
        profile="personal",
        region="us-west-2",
    )


def test_read_file(cloudfront_parser):
    entries = cloudfront_parser.read_file("test/data/cloudfront-multiple.log")
    assert len(list(entries)) == 6


def test_read_files(cloudfront_parser):
    entries = cloudfront_parser.read_files(["test/data/cloudfront-multiple.log"])
    assert len(list(entries)) == 6


def test_read_s3(monkeypatch, cloudfront_parser):

    monkeypatch.setattr(S3Service, "client", MockS3Client())

    entries = cloudfront_parser.read_s3(
        "aws-logs-test-data",
        "cloudfront-multiple.log",
    )
    assert len(list(entries)) == 6


def test_read_url(cloudfront_parser):
    entries = cloudfront_parser.read_url(
        "s3://aws-logs-test-data/cloudfront-multiple.log"
    )
    assert len(list(entries)) == 6
