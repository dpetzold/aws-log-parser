import pytest

from aws_log_parser import (
    AwsLogParser,
    LogType,
)


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


def test_read_s3(cloudfront_parser):
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
