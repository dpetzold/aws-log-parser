from aws_log_parser import (
    AwsLogParser,
    LogType,
)


def test_read_file():
    AwsLogParser(LogType.ClassicLoadBalancer).read_file(
        "test/data/cloudfront-multiple.log"
    )


def test_read_files():
    AwsLogParser(LogType.ClassicLoadBalancer).read_files("test/data")


def test_read_s3():
    AwsLogParser(LogType.ClassicLoadBalancer).read_s3(
        "aws-logs-test-data",
        "cloudfront-multiple.log",
    )


def test_read_url():
    AwsLogParser(LogType.ClassicLoadBalancer).read_url(
        "s3://aws-logs-test-data/cloudfront-multiple.log"
    )
