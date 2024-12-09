import datetime
import pytest


from aws_log_parser import AwsLogParser
from aws_log_parser.models import (
    CloudFrontWebDistributionLogEntry,
)


def parse_entry(contents, log_type):
    return list(AwsLogParser(log_type).parse(contents))[0]


@pytest.fixture
def cookie_zip_code():
    return {"zip": "98101"}


@pytest.fixture
def cookie_with_space():
    return {"this zip": "98101"}


@pytest.fixture
def cookie_empty():
    return {}


@pytest.fixture
def base_cloudfront_log_entry():
    return CloudFrontWebDistributionLogEntry(
        date=datetime.date(2014, 5, 23),
        time=datetime.time(1, 13, 11),
        edge_location="FRA2",
        sent_bytes=182,
        client_ip="192.0.2.10",
        http_method="GET",
        host="d111111abcdef8.cloudfront.net",
        uri_stem="/view/my/file.html",
        status_code=200,
        referrer="www.displaymyfiles.com",
        user_agent="Mozilla/4.0 (compatible; MSIE 5.0b1; Mac_PowerPC)",
        uri_query=None,
        cookie=None,
        edge_result_type="RefreshHit",
        edge_request_id="MRVMF7KydIvxMWfJIglgwHQwZsbG2IhRJ07sn9AkKUFSHS9EXAMPLE==",
        host_header="d111111abcdef8.cloudfront.net",
        protocol="http",
        received_bytes=None,
        time_taken=0.001,
        forwarded_for=None,
        ssl_protocol=None,
        ssl_cipher=None,
        edge_response_result_type="RefreshHit",
        protocol_version="HTTP/1.1",
    )


def fixture(shared_datadir, fixture_name):
    return (shared_datadir / fixture_name).open()


def log_entry(shared_datadir, test_name):
    return fixture(shared_datadir, f"{test_name}.csv")


@pytest.fixture
def waf_entry_json(shared_datadir):
    return fixture(shared_datadir, "waf_log.json").read()


@pytest.fixture
def cloudfront_entry(shared_datadir):
    return log_entry(shared_datadir, cloudfront_entry.__name__)


@pytest.fixture
def cloudfront_entry_broken_cookie(shared_datadir):
    return log_entry(shared_datadir, cloudfront_entry_broken_cookie.__name__)


@pytest.fixture
def cloudfront_entry_cookie_with_encoding(shared_datadir):
    return log_entry(shared_datadir, cloudfront_entry_cookie_with_encoding.__name__)


@pytest.fixture
def cloudfront_entry2(shared_datadir):
    return log_entry(shared_datadir, cloudfront_entry2.__name__)


@pytest.fixture
def loadbalancer_http_entry(shared_datadir):
    return log_entry(shared_datadir, loadbalancer_http_entry.__name__)


@pytest.fixture
def loadbalancer_https_entry(shared_datadir):
    return log_entry(shared_datadir, loadbalancer_https_entry.__name__)


@pytest.fixture
def loadbalancer_http2_entry(shared_datadir):
    return log_entry(shared_datadir, loadbalancer_http2_entry.__name__)


@pytest.fixture
def loadbalancer_http2_entry_auth_error(shared_datadir):
    return log_entry(shared_datadir, loadbalancer_http2_entry_auth_error.__name__)


@pytest.fixture
def loadbalancer_http2_entry_auth_missing(shared_datadir):
    return log_entry(shared_datadir, loadbalancer_http2_entry_auth_missing.__name__)


@pytest.fixture
def loadbalancer_websockets_entry(shared_datadir):
    return log_entry(shared_datadir, loadbalancer_websockets_entry.__name__)


@pytest.fixture
def loadbalancer_secured_websockets_entry(shared_datadir):
    return log_entry(shared_datadir, loadbalancer_secured_websockets_entry.__name__)


@pytest.fixture
def loadbalancer_lambda_entry(shared_datadir):
    return log_entry(shared_datadir, loadbalancer_lambda_entry.__name__)


@pytest.fixture
def loadbalancer_lambda_failed_entry(shared_datadir):
    return log_entry(shared_datadir, loadbalancer_lambda_failed_entry.__name__)


@pytest.fixture
def loadbalancer_cloudfront_forward(shared_datadir):
    return log_entry(shared_datadir, loadbalancer_cloudfront_forward.__name__)


@pytest.fixture
def loadbalancer_cloudfront_forward_refused(shared_datadir):
    return log_entry(shared_datadir, loadbalancer_cloudfront_forward_refused.__name__)


@pytest.fixture
def loadbalancer_cloudfront_forward_h2(shared_datadir):
    return log_entry(shared_datadir, loadbalancer_cloudfront_forward_h2.__name__)


@pytest.fixture
def classic_loadbalancer_http_entry(shared_datadir):
    return log_entry(shared_datadir, classic_loadbalancer_http_entry.__name__)
