import datetime
import dataclasses


from .conftest import parse_entry

from aws_log_parser.models import (
    CloudFrontWebDistributionLogEntry,
    LogType,
)


def test_cloudfront_entry(base_cloudfront_log_entry, cloudfront_entry, cookie_zip_code):
    replaced = dataclasses.replace(base_cloudfront_log_entry, cookie=cookie_zip_code)
    entry = CloudFrontWebDistributionLogEntry(
        **dataclasses.asdict(parse_entry(cloudfront_entry, LogType.CloudFront))
    )
    assert entry == replaced
    assert isinstance(entry.timestamp, datetime.datetime) is True
    assert entry.timestamp == datetime.datetime(
        2014, 5, 23, 1, 13, 11, tzinfo=datetime.timezone.utc
    )


def test_cloudfront_entry_broken_cookie(
    base_cloudfront_log_entry, cloudfront_entry_broken_cookie, cookie_empty
):
    replaced = dataclasses.replace(base_cloudfront_log_entry, cookie=cookie_empty)
    entry = CloudFrontWebDistributionLogEntry(
        **dataclasses.asdict(
            parse_entry(cloudfront_entry_broken_cookie, LogType.CloudFront)
        )
    )
    assert entry == replaced
    assert isinstance(entry.timestamp, datetime.datetime) is True
    assert entry.timestamp == datetime.datetime(
        2014, 5, 23, 1, 13, 11, tzinfo=datetime.timezone.utc
    )


def test_cloudfront_entry_cookie_with_encoding(
    base_cloudfront_log_entry, cloudfront_entry_cookie_with_encoding, cookie_with_space
):
    replaced = dataclasses.replace(base_cloudfront_log_entry, cookie=cookie_with_space)
    entry = CloudFrontWebDistributionLogEntry(
        **dataclasses.asdict(
            parse_entry(cloudfront_entry_cookie_with_encoding, LogType.CloudFront)
        )
    )
    assert entry == replaced
    assert isinstance(entry.timestamp, datetime.datetime) is True
    assert entry.timestamp == datetime.datetime(
        2014, 5, 23, 1, 13, 11, tzinfo=datetime.timezone.utc
    )


def test_cloudfront_entry2(
    base_cloudfront_log_entry, cloudfront_entry2, cookie_zip_code
):
    cloudfront_log_entry2 = dataclasses.replace(
        base_cloudfront_log_entry,
        time=datetime.time(1, 13, 12),
        edge_location="LAX1",
        sent_bytes=2390282,
        cookie=cookie_zip_code,
        client_ip="192.0.2.202",
        uri_stem="/soundtrack/happy.mp3",
        status_code=304,
        referrer="www.unknownsingers.com",
        uri_query={"a": ["b"], "c": ["d"]},
        edge_result_type="Hit",
        edge_response_result_type="Hit",
        time_taken=0.002,
        user_agent="Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
        edge_request_id="xGN7KWpVEmB9Dp7ctcVFQC4E-nrcOcEKS3QyAez--06dV7TEXAMPLE==",
    )
    entry = parse_entry(cloudfront_entry2, LogType.CloudFront)
    assert entry == cloudfront_log_entry2
