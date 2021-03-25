import datetime


from .conftest import parse_entry

from aws_log_parser.models import LogType


def test_cloudfront_entry(base_cloudfront_log_entry, cloudfront_entry, cookie_zip_code):
    base_cloudfront_log_entry.cookie = cookie_zip_code
    entry = parse_entry(cloudfront_entry, LogType.CloudFront)
    assert entry == base_cloudfront_log_entry
    assert isinstance(entry.timestamp, datetime.datetime) is True
    assert entry.timestamp == datetime.datetime(
        2014, 5, 23, 1, 13, 11, tzinfo=datetime.timezone.utc
    )


def test_cloudfront_entry_broken_cookie(
    base_cloudfront_log_entry, cloudfront_entry_broken_cookie, cookie_empty
):
    base_cloudfront_log_entry.cookie = cookie_empty
    entry = parse_entry(cloudfront_entry_broken_cookie, LogType.CloudFront)
    assert entry == base_cloudfront_log_entry
    assert isinstance(entry.timestamp, datetime.datetime) is True
    assert entry.timestamp == datetime.datetime(
        2014, 5, 23, 1, 13, 11, tzinfo=datetime.timezone.utc
    )


def test_cloudfront_entry_cookie_with_encoding(
    base_cloudfront_log_entry, cloudfront_entry_cookie_with_encoding, cookie_with_space
):
    base_cloudfront_log_entry.cookie = cookie_with_space
    entry = parse_entry(cloudfront_entry_cookie_with_encoding, LogType.CloudFront)
    assert entry == base_cloudfront_log_entry
    assert isinstance(entry.timestamp, datetime.datetime) is True
    assert entry.timestamp == datetime.datetime(
        2014, 5, 23, 1, 13, 11, tzinfo=datetime.timezone.utc
    )


def test_cloudfront_entry2(
    base_cloudfront_log_entry, cloudfront_entry2, cookie_zip_code
):

    base_cloudfront_log_entry.time = datetime.time(1, 13, 12)
    base_cloudfront_log_entry.edge_location = "LAX1"
    base_cloudfront_log_entry.sent_bytes = 2390282
    base_cloudfront_log_entry.cookie = cookie_zip_code
    base_cloudfront_log_entry.client_ip = "192.0.2.202"
    base_cloudfront_log_entry.uri_stream = "/soundtrack/happy.mp3"
    base_cloudfront_log_entry.status_code = 304
    base_cloudfront_log_entry.referrer = "www.unknownsingers.com"
    base_cloudfront_log_entry.uri_query = {"a": ["b"], "c": ["d"]}
    base_cloudfront_log_entry.edge_result_type = "Hit"
    base_cloudfront_log_entry.edge_response_result_type = "Hit"
    base_cloudfront_log_entry.time_taken = 0.002
    base_cloudfront_log_entry.user_agent = (
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)"
    )
    base_cloudfront_log_entry.edge_request_id = (
        "xGN7KWpVEmB9Dp7ctcVFQC4E-nrcOcEKS3QyAez--06dV7TEXAMPLE=="
    )
    entry = parse_entry(cloudfront_entry2, LogType.CloudFront)
    assert entry == base_cloudfront_log_entry
