import datetime
import user_agents
import pytest

from user_agents.parsers import UserAgent

from aws_log_parser.models import (  # CloudFrontRTMPDistributionLogEntry,
    CloudFrontWebDistributionLogEntry,
    LoadBalancerLogEntry,
    LoadBalancerErrorReason,
    LogType,
    HttpType,
    HttpRequest,
    Host,
)
from aws_log_parser.parser import log_parser


def parse_entry(contents, log_type):
    return list(log_parser(contents, log_type))[0]


@pytest.fixture
def curl_fixture():
    return user_agents.parse('curl/7.46.0')


@pytest.fixture(autouse=True)
def patch_user_agent(monkeypatch):
    def __eq__(self, obj):
        return self.ua_string == obj.ua_string
    monkeypatch.setattr(UserAgent, '__eq__', __eq__)


def test_loadbalancer_cloudfront_forward_h2(loadbalancer_cloudfront_forward_h2, curl_fixture):
    entry = parse_entry(loadbalancer_cloudfront_forward_h2, LogType.LoadBalancer)
    assert entry == LoadBalancerLogEntry(
        http_type=HttpType('h2'),
        timestamp=datetime.datetime(
            2018, 11, 30, 22, 23, 0, 186641,
            tzinfo=datetime.timezone.utc,
        ),
        elb='app/my-loadbalancer/50dc6c495c0c9188',
        client=Host(ip='192.168.131.39', port=2817),
        target=None,
        request_processing_time=0.000,
        target_processing_time=0.001,
        response_processing_time=0.000,
        elb_status_code=502,
        target_status_code=None,
        received_bytes=34,
        sent_bytes=366,
        http_request=HttpRequest(
            method='GET',
            url='http://www.example.com:80/',
            query={},
            protocol='HTTP/1.1',
        ),
        user_agent=curl_fixture,
        ssl_cipher=None,
        ssl_protocol=None,
        target_group_arn='arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067',
        trace_id='Root=1-58337364-23a8c76965a2ef7629b185e3',
        domain_name='api.example.com',
        chosen_cert_arn=None,
        matched_rule_priority=0,
        request_creation_time=datetime.datetime(
            2018, 11, 30, 22, 22, 48, 364000,
            tzinfo=datetime.timezone.utc,
        ),
        actions_executed=['waf', 'forward'],
        redirect_url=None,
        error_reason=None,
    )


def test_loadbalancer_cloudfront_forward(loadbalancer_cloudfront_forward, curl_fixture):
    entry = parse_entry(loadbalancer_cloudfront_forward, LogType.LoadBalancer)
    assert entry == LoadBalancerLogEntry(
        http_type=HttpType('http'),
        timestamp=datetime.datetime(
            2018, 11, 30, 22, 23, 0, 186641,
            tzinfo=datetime.timezone.utc,
        ),
        elb='app/my-loadbalancer/50dc6c495c0c9188',
        client=Host(ip='192.168.131.39', port=2817),
        target=None,
        request_processing_time=0.000,
        target_processing_time=0.001,
        response_processing_time=0.000,
        elb_status_code=502,
        target_status_code=None,
        received_bytes=34,
        sent_bytes=366,
        http_request=HttpRequest(
            method='GET',
            url='http://www.example.com:80/',
            query={},
            protocol='HTTP/1.1',
        ),
        user_agent=curl_fixture,
        ssl_cipher=None,
        ssl_protocol=None,
        target_group_arn='arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067',
        trace_id='Root=1-58337364-23a8c76965a2ef7629b185e3',
        domain_name=None,
        chosen_cert_arn=None,
        matched_rule_priority=0,
        request_creation_time=datetime.datetime(
            2018, 11, 30, 22, 22, 48, 364000,
            tzinfo=datetime.timezone.utc,
        ),
        actions_executed=['waf', 'forward'],
        redirect_url=None,
        error_reason=None,
    )


def test_loadbalancer_cloudfront_forward_refused(
    loadbalancer_cloudfront_forward_refused,
    curl_fixture,
):
    entry = parse_entry(loadbalancer_cloudfront_forward_refused, LogType.LoadBalancer)
    assert entry == LoadBalancerLogEntry(
        http_type=HttpType('http'),
        timestamp=datetime.datetime(
            2018, 11, 30, 22, 23, 0, 186641,
            tzinfo=datetime.timezone.utc,
        ),
        elb='app/my-loadbalancer/50dc6c495c0c9188',
        client=Host(ip='192.168.131.39', port=2817),
        target=None,
        request_processing_time=0.000,
        target_processing_time=0.001,
        response_processing_time=0.000,
        elb_status_code=502,
        target_status_code=None,
        received_bytes=34,
        sent_bytes=366,
        http_request=HttpRequest(
            method='GET',
            url='http://www.example.com:80/',
            query={},
            protocol='HTTP/1.1',
        ),
        user_agent=curl_fixture,
        ssl_cipher=None,
        ssl_protocol=None,
        target_group_arn='arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067',
        trace_id='Root=1-58337364-23a8c76965a2ef7629b185e3',
        domain_name='api.example.com',
        chosen_cert_arn='session-reused',
        matched_rule_priority=0,
        request_creation_time=datetime.datetime(
            2018, 11, 30, 22, 22, 48, 364000,
            tzinfo=datetime.timezone.utc,
        ),
        actions_executed=['waf', 'forward'],
        redirect_url=None,
        error_reason=None,
    )


def test_cloudfront_entry(cloudfront_entry, cookie_zip_code):
    entry = parse_entry(cloudfront_entry, LogType.CloudFront)
    assert entry == CloudFrontWebDistributionLogEntry(
        date=datetime.date(2014, 5, 23),
        time=datetime.time(1, 13, 11),
        edge_location='FRA2',
        sent_bytes=182,
        client_ip='192.0.2.10',
        http_method='GET',
        host='d111111abcdef8.cloudfront.net',
        uri='/view/my/file.html',
        status_code=200,
        referrer='www.displaymyfiles.com',
        user_agent='Mozilla/4.0%20(compatible;%20MSIE%205.0b1;%20Mac_PowerPC)',
        uri_query=None,
        cookie='zip=98101',
        edge_result_type='RefreshHit',
        edge_request_id='MRVMF7KydIvxMWfJIglgwHQwZsbG2IhRJ07sn9AkKUFSHS9EXAMPLE==',
        host_header='d111111abcdef8.cloudfront.net',
        protocol='http',
        received_bytes=None,
        time_taken=0.001,
        forwarded_for=None,
        ssl_protocol=None,
        ssl_cipher=None,
        edge_response_result_type='RefreshHit',
        protocol_version='HTTP/1.1',
        fle_encrypted_fields='',
    )
    assert isinstance(entry.timestamp, datetime.datetime) is True
    assert entry.timestamp == datetime.datetime(2014, 5, 23, 1, 13, 11, tzinfo=datetime.timezone.utc)


def test_cloudfront_entry_broken_cookie(cloudfront_entry_broken_cookie, cookie_empty):
    entry = parse_entry(cloudfront_entry_broken_cookie, LogType.CloudFront)
    assert entry == CloudFrontWebDistributionLogEntry(
        date=datetime.date(2014, 5, 23),
        time=datetime.time(1, 13, 11),
        edge_location='FRA2',
        sent_bytes=182,
        client_ip='192.0.2.10',
        http_method='GET',
        host='d111111abcdef8.cloudfront.net',
        uri='/view/my/file.html',
        status_code=200,
        referrer='www.displaymyfiles.com',
        user_agent='Mozilla/4.0%20(compatible;%20MSIE%205.0b1;%20Mac_PowerPC)',
        uri_query=None,
        cookie='zip 98101',
        edge_result_type='RefreshHit',
        edge_request_id='MRVMF7KydIvxMWfJIglgwHQwZsbG2IhRJ07sn9AkKUFSHS9EXAMPLE==',
        host_header='d111111abcdef8.cloudfront.net',
        protocol='http',
        received_bytes=None,
        time_taken=0.001,
        forwarded_for=None,
        ssl_protocol=None,
        ssl_cipher=None,
        edge_response_result_type='RefreshHit',
        protocol_version='HTTP/1.1',
        fle_encrypted_fields='',
    )
    assert isinstance(entry.timestamp, datetime.datetime) is True
    assert entry.timestamp == datetime.datetime(2014, 5, 23, 1, 13, 11, tzinfo=datetime.timezone.utc)


def test_cloudfront_entry2(cloudfront_entry2, cookie_zip_code):
    entry = parse_entry(cloudfront_entry2, LogType.CloudFront)
    assert entry == CloudFrontWebDistributionLogEntry(
        date=datetime.date(2014, 5, 23),
        time=datetime.time(1, 13, 12),
        edge_location='LAX1',
        sent_bytes=2390282,
        client_ip='192.0.2.202',
        http_method='GET',
        host='d111111abcdef8.cloudfront.net',
        uri='/soundtrack/happy.mp3',
        status_code=304,
        referrer='www.unknownsingers.com',
        user_agent='Mozilla/4.0%20(compatible;%20MSIE%207.0;%20Windows%20NT%205.1)',
        uri_query='a=b&c=d',
        cookie='zip=98101',
        edge_result_type='Hit',
        edge_request_id='xGN7KWpVEmB9Dp7ctcVFQC4E-nrcOcEKS3QyAez--06dV7TEXAMPLE==',
        host_header='d111111abcdef8.cloudfront.net',
        protocol='http',
        received_bytes=None,
        time_taken=0.002,
        forwarded_for=None,
        ssl_protocol=None,
        ssl_cipher=None,
        edge_response_result_type='Hit',
        protocol_version='HTTP/1.1',
        fle_encrypted_fields='',
    )


def test_loadbalancer_http_entry(loadbalancer_http_entry, curl_fixture):
    entry = parse_entry(loadbalancer_http_entry, LogType.LoadBalancer)
    assert entry == LoadBalancerLogEntry(
        http_type=HttpType('http'),
        timestamp=datetime.datetime(
            2018, 7, 2, 22, 23, 0, 186641,
            tzinfo=datetime.timezone.utc,
        ),
        elb='app/my-loadbalancer/50dc6c495c0c9188',
        client=Host(ip='192.168.131.39', port=2817),
        target=Host(ip='10.0.0.1', port=80),
        request_processing_time=0.000,
        target_processing_time=0.001,
        response_processing_time=0.000,
        elb_status_code=200,
        target_status_code=200,
        received_bytes=34,
        sent_bytes=366,
        http_request=HttpRequest(
            method='GET',
            url='http://www.example.com:80/?a=b&c=d&zip=98101',
            query={'a': ['b'], 'c': ['d'], 'zip': ['98101']},
            protocol='HTTP/1.1',
        ),
        user_agent=curl_fixture,
        ssl_cipher=None,
        ssl_protocol=None,
        target_group_arn='arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067',
        trace_id='Root=1-58337262-36d228ad5d99923122bbe354',
        domain_name=None,
        chosen_cert_arn=None,
        matched_rule_priority=0,
        request_creation_time=datetime.datetime(
            2018, 7, 2, 22, 22, 48, 364000,
            tzinfo=datetime.timezone.utc,
        ),
        actions_executed=['forward'],
        redirect_url=None,
        error_reason=None,
    )


def test_loadbalancer_https_entry(loadbalancer_https_entry, curl_fixture):
    entry = parse_entry(loadbalancer_https_entry, LogType.LoadBalancer)
    assert entry == LoadBalancerLogEntry(
        http_type=HttpType('https'),
        timestamp=datetime.datetime(
            2018, 7, 2, 22, 23, 0, 186641,
            tzinfo=datetime.timezone.utc,
        ),
        elb='app/my-loadbalancer/50dc6c495c0c9188',
        client=Host(ip='192.168.131.39', port=2817),
        target=Host(ip='10.0.0.1', port=80),
        request_processing_time=0.086,
        target_processing_time=0.048,
        response_processing_time=0.037,
        elb_status_code=200,
        target_status_code=200,
        received_bytes=0,
        sent_bytes=57,
        http_request=HttpRequest(
            method='GET',
            url='https://www.example.com:443/',
            query={},
            protocol='HTTP/1.1',
        ),
        user_agent=curl_fixture,
        ssl_cipher='ECDHE-RSA-AES128-GCM-SHA256',
        ssl_protocol='TLSv1.2',
        target_group_arn='arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067',
        trace_id='Root=1-58337281-1d84f3d73c47ec4e58577259',
        domain_name='www.example.com',
        chosen_cert_arn='arn:aws:acm:us-east-2:123456789012:certificate/12345678-1234-1234-1234-123456789012',
        matched_rule_priority=1,
        request_creation_time=datetime.datetime(
            2018, 7, 2, 22, 22, 48, 364000,
            tzinfo=datetime.timezone.utc,
        ),
        actions_executed=['authenticate', 'forward'],
        redirect_url=None,
        error_reason=None,
    )


def test_loadbalancer_http2_entry(loadbalancer_http2_entry, curl_fixture):
    entry = parse_entry(loadbalancer_http2_entry, LogType.LoadBalancer)
    assert entry == LoadBalancerLogEntry(
        http_type=HttpType('h2'),
        timestamp=datetime.datetime(
            2018, 7, 2, 22, 23, 0, 186641,
            tzinfo=datetime.timezone.utc,
        ),
        elb='app/my-loadbalancer/50dc6c495c0c9188',
        client=Host(ip='10.0.1.252', port=48160),
        target=Host(ip='10.0.0.66', port=9000),
        request_processing_time=0.000,
        target_processing_time=0.002,
        response_processing_time=0.000,
        elb_status_code=200,
        target_status_code=200,
        received_bytes=5,
        sent_bytes=257,
        http_request=HttpRequest(
            method='GET',
            url='https://10.0.2.105:773/',
            query={},
            protocol='HTTP/2.0',
        ),
        user_agent=curl_fixture,
        ssl_cipher='ECDHE-RSA-AES128-GCM-SHA256',
        ssl_protocol='TLSv1.2',
        target_group_arn='arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067',
        trace_id='Root=1-58337327-72bd00b0343d75b906739c42',
        domain_name=None,
        chosen_cert_arn=None,
        matched_rule_priority=1,
        request_creation_time=datetime.datetime(
            2018, 7, 2, 22, 22, 48, 364000,
            tzinfo=datetime.timezone.utc,
        ),
        actions_executed=['redirect'],
        redirect_url='https://example.com:80/',
        error_reason=None,
    )


def test_loadbalancer_websockets_entry(loadbalancer_websockets_entry):
    entry = parse_entry(loadbalancer_websockets_entry, LogType.LoadBalancer)
    assert entry == LoadBalancerLogEntry(
        http_type=HttpType('ws'),
        timestamp=datetime.datetime(
            2018, 7, 2, 22, 23, 0, 186641,
            tzinfo=datetime.timezone.utc,
        ),
        elb='app/my-loadbalancer/50dc6c495c0c9188',
        client=Host(ip='10.0.0.140', port=40914),
        target=Host(ip='10.0.1.192', port=8010),
        request_processing_time=0.001,
        target_processing_time=0.003,
        response_processing_time=0.000,
        elb_status_code=101,
        target_status_code=101,
        received_bytes=218,
        sent_bytes=587,
        http_request=HttpRequest(
            method='GET',
            url='http://10.0.0.30:80/',
            query={},
            protocol='HTTP/1.1',
        ),
        user_agent=None,
        ssl_cipher=None,
        ssl_protocol=None,
        target_group_arn='arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067',
        trace_id='Root=1-58337364-23a8c76965a2ef7629b185e3',
        domain_name=None,
        chosen_cert_arn=None,
        matched_rule_priority=1,
        request_creation_time=datetime.datetime(
            2018, 7, 2, 22, 22, 48, 364000,
            tzinfo=datetime.timezone.utc,
        ),
        actions_executed=['forward'],
        redirect_url=None,
        error_reason=None,
    )


def test_loadbalancer_secured_websockets_entry(loadbalancer_secured_websockets_entry):
    entry = parse_entry(loadbalancer_secured_websockets_entry, LogType.LoadBalancer)
    assert entry == LoadBalancerLogEntry(
        http_type=HttpType('wss'),
        timestamp=datetime.datetime(
            2018, 7, 2, 22, 23, 0, 186641,
            tzinfo=datetime.timezone.utc,
        ),
        elb='app/my-loadbalancer/50dc6c495c0c9188',
        client=Host(ip='10.0.0.140', port=44244),
        target=Host(ip='10.0.0.171', port=8010),
        request_processing_time=0.000,
        target_processing_time=0.001,
        response_processing_time=0.000,
        elb_status_code=101,
        target_status_code=101,
        received_bytes=218,
        sent_bytes=786,
        http_request=HttpRequest(
            method='GET',
            url='https://10.0.0.30:443/',
            query={},
            protocol='HTTP/1.1',
        ),
        user_agent=None,
        ssl_cipher='ECDHE-RSA-AES128-GCM-SHA256',
        ssl_protocol='TLSv1.2',
        target_group_arn='arn:aws:elasticloadbalancing:us-west-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067',
        trace_id='Root=1-58337364-23a8c76965a2ef7629b185e3',
        domain_name=None,
        chosen_cert_arn=None,
        matched_rule_priority=1,
        request_creation_time=datetime.datetime(
            2018, 7, 2, 22, 22, 48, 364000,
            tzinfo=datetime.timezone.utc,
        ),
        actions_executed=['forward'],
        redirect_url=None,
        error_reason=None,
    )


def test_loadbalancer_lambda_entry(loadbalancer_lambda_entry, curl_fixture):
    entry = parse_entry(loadbalancer_lambda_entry, LogType.LoadBalancer)
    assert entry == LoadBalancerLogEntry(
        http_type=HttpType('http'),
        timestamp=datetime.datetime(
            2018, 11, 30, 22, 23, 0, 186641,
            tzinfo=datetime.timezone.utc,
        ),
        elb='app/my-loadbalancer/50dc6c495c0c9188',
        client=Host(ip='192.168.131.39', port=2817),
        target=None,
        request_processing_time=0.000,
        target_processing_time=0.001,
        response_processing_time=0.000,
        elb_status_code=200,
        target_status_code=200,
        received_bytes=34,
        sent_bytes=366,
        http_request=HttpRequest(
            method='GET',
            url='http://www.example.com:80/',
            query={},
            protocol='HTTP/1.1',
        ),
        user_agent=curl_fixture,
        ssl_cipher=None,
        ssl_protocol=None,
        target_group_arn='arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067',
        trace_id='Root=1-58337364-23a8c76965a2ef7629b185e3',
        domain_name=None,
        chosen_cert_arn=None,
        matched_rule_priority=0,
        request_creation_time=datetime.datetime(
            2018, 11, 30, 22, 22, 48, 364000,
            tzinfo=datetime.timezone.utc,
        ),
        actions_executed=['forward'],
        redirect_url=None,
        error_reason=None,
    )


def test_loadbalancer_lambda_failed_entry(loadbalancer_lambda_failed_entry, curl_fixture):
    entry = parse_entry(loadbalancer_lambda_failed_entry, LogType.LoadBalancer)
    assert entry == LoadBalancerLogEntry(
        http_type=HttpType('http'),
        timestamp=datetime.datetime(
            2018, 11, 30, 22, 23, 0, 186641,
            tzinfo=datetime.timezone.utc,
        ),
        elb='app/my-loadbalancer/50dc6c495c0c9188',
        client=Host(ip='192.168.131.39', port=2817),
        target=None,
        request_processing_time=0.000,
        target_processing_time=0.001,
        response_processing_time=0.000,
        elb_status_code=502,
        target_status_code=None,
        received_bytes=34,
        sent_bytes=366,
        http_request=HttpRequest(
            method='GET',
            url='http://www.example.com:80/',
            query={},
            protocol='HTTP/1.1',
        ),
        user_agent=curl_fixture,
        ssl_cipher=None,
        ssl_protocol=None,
        target_group_arn='arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067',
        trace_id='Root=1-58337364-23a8c76965a2ef7629b185e3',
        domain_name=None,
        chosen_cert_arn=None,
        matched_rule_priority=0,
        request_creation_time=datetime.datetime(
            2018, 11, 30, 22, 22, 48, 364000,
            tzinfo=datetime.timezone.utc,
        ),
        actions_executed=['forward'],
        redirect_url=None,
        error_reason=LoadBalancerErrorReason.LambdaInvalidResponse,
    )
