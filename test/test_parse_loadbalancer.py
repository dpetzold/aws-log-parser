import dataclasses
import datetime
import pytest

from aws_log_parser.models import (
    Host,
    HttpRequest,
    HttpType,
    LoadBalancerErrorReason,
    LoadBalancerLogEntry,
    LogType,
    ClassicLoadBalancerLogEntry,
)


from .conftest import parse_entry


@pytest.fixture
def base_load_balancer_log_entry():
    return LoadBalancerLogEntry(
        type=HttpType.H2,
        timestamp=datetime.datetime(
            2018,
            11,
            30,
            22,
            23,
            0,
            186641,
            tzinfo=datetime.timezone.utc,
        ),
        elb="app/my-loadbalancer/50dc6c495c0c9188",
        client=Host(
            ip="192.168.131.39",
            port=2817,
        ),
        target=None,
        request_processing_time=0.0,
        target_processing_time=0.001,
        response_processing_time=0.0,
        elb_status_code=502,
        target_status_code=None,
        received_bytes=34,
        sent_bytes=366,
        http_request=HttpRequest(
            method="GET",
            url="http://www.example.com:80/",
            path="/",
            query={},
            protocol="HTTP/1.1",
        ),
        user_agent="curl/7.46.0",
        ssl_cipher=None,
        ssl_protocol=None,
        target_group_arn="arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067",
        trace_id="Root=1-58337364-23a8c76965a2ef7629b185e3",
        domain_name="api.example.com",
        chosen_cert_arn=None,
        matched_rule_priority=0,
        request_creation_time=datetime.datetime(
            2018,
            11,
            30,
            22,
            22,
            48,
            364000,
            tzinfo=datetime.timezone.utc,
        ),
        actions_executed=["waf", "forward"],
        redirect_url=None,
        error_reason=None,
    )


def test_loadbalancer_cloudfront_forward_h2(
    base_load_balancer_log_entry, loadbalancer_cloudfront_forward_h2
):
    entry = parse_entry(loadbalancer_cloudfront_forward_h2, LogType.LoadBalancer)
    assert entry == base_load_balancer_log_entry


def test_loadbalancer_cloudfront_forward(
    base_load_balancer_log_entry, loadbalancer_cloudfront_forward
):
    log_entry = dataclasses.replace(
        base_load_balancer_log_entry, domain_name=None, type=HttpType.Http
    )
    entry = parse_entry(loadbalancer_cloudfront_forward, LogType.LoadBalancer)
    assert entry == log_entry


def test_loadbalancer_cloudfront_forward_refused(
    base_load_balancer_log_entry,
    loadbalancer_cloudfront_forward_refused,
):
    log_entry = dataclasses.replace(
        base_load_balancer_log_entry,
        type=HttpType.Http,
        chosen_cert_arn="session-reused",
    )
    entry = parse_entry(loadbalancer_cloudfront_forward_refused, LogType.LoadBalancer)
    assert entry == log_entry


def test_loadbalancer_http_entry(loadbalancer_http_entry):
    entry = parse_entry(loadbalancer_http_entry, LogType.LoadBalancer)
    assert entry == LoadBalancerLogEntry(
        type=HttpType.Http,
        timestamp=datetime.datetime(
            2018, 7, 2, 22, 23, 0, 186641, tzinfo=datetime.timezone.utc
        ),
        elb="app/my-loadbalancer/50dc6c495c0c9188",
        client=Host(
            ip="192.168.131.39",
            port=2817,
        ),
        target=Host(
            ip="10.0.0.1",
            port=80,
        ),
        request_processing_time=0.0,
        target_processing_time=0.001,
        response_processing_time=0.0,
        elb_status_code=200,
        target_status_code=200,
        received_bytes=34,
        sent_bytes=366,
        http_request=HttpRequest(
            method="GET",
            url="http://www.example.com:80/?a=b&c=d&zip=98101",
            path="/",
            query={
                "a": ["b"],
                "c": ["d"],
                "zip": ["98101"],
            },
            protocol="HTTP/1.1",
        ),
        user_agent="curl/7.46.0",
        ssl_cipher=None,
        ssl_protocol=None,
        target_group_arn="arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067",
        trace_id="Root=1-58337262-36d228ad5d99923122bbe354",
        domain_name=None,
        chosen_cert_arn=None,
        matched_rule_priority=0,
        request_creation_time=datetime.datetime(
            2018, 7, 2, 22, 22, 48, 364000, tzinfo=datetime.timezone.utc
        ),
        actions_executed=["forward"],
        redirect_url=None,
        error_reason=None,
    )


def test_loadbalancer_https_entry(loadbalancer_https_entry):
    entry = parse_entry(loadbalancer_https_entry, LogType.LoadBalancer)
    assert entry == LoadBalancerLogEntry(
        type=HttpType.Https,
        timestamp=datetime.datetime(
            2018, 7, 2, 22, 23, 0, 186641, tzinfo=datetime.timezone.utc
        ),
        elb="app/my-loadbalancer/50dc6c495c0c9188",
        client=Host(
            ip="192.168.131.39",
            port=2817,
        ),
        target=Host(
            ip="10.0.0.1",
            port=80,
        ),
        request_processing_time=0.086,
        target_processing_time=0.048,
        response_processing_time=0.037,
        elb_status_code=200,
        target_status_code=200,
        received_bytes=0,
        sent_bytes=57,
        http_request=HttpRequest(
            method="GET",
            url="https://www.example.com:443/",
            path="/",
            query={},
            protocol="HTTP/1.1",
        ),
        user_agent="curl/7.46.0",
        ssl_cipher="ECDHE-RSA-AES128-GCM-SHA256",
        ssl_protocol="TLSv1.2",
        target_group_arn="arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067",
        trace_id="Root=1-58337281-1d84f3d73c47ec4e58577259",
        domain_name="www.example.com",
        chosen_cert_arn="arn:aws:acm:us-east-2:123456789012:certificate/12345678-1234-1234-1234-123456789012",
        matched_rule_priority=1,
        request_creation_time=datetime.datetime(
            2018, 7, 2, 22, 22, 48, 364000, tzinfo=datetime.timezone.utc
        ),
        actions_executed=["authenticate", "forward"],
        redirect_url=None,
        error_reason=None,
    )


def test_loadbalancer_http2_entry(loadbalancer_http2_entry):
    entry = parse_entry(loadbalancer_http2_entry, LogType.LoadBalancer)
    assert entry == LoadBalancerLogEntry(
        type=HttpType.H2,
        timestamp=datetime.datetime(
            2018, 7, 2, 22, 23, 0, 186641, tzinfo=datetime.timezone.utc
        ),
        elb="app/my-loadbalancer/50dc6c495c0c9188",
        client=Host(
            ip="10.0.1.252",
            port=48160,
        ),
        target=Host(
            ip="10.0.0.66",
            port=9000,
        ),
        request_processing_time=0.0,
        target_processing_time=0.002,
        response_processing_time=0.0,
        elb_status_code=200,
        target_status_code=200,
        received_bytes=5,
        sent_bytes=257,
        http_request=HttpRequest(
            method="GET",
            url="https://10.0.2.105:773/",
            path="/",
            query={},
            protocol="HTTP/2.0",
        ),
        user_agent="curl/7.46.0",
        ssl_cipher="ECDHE-RSA-AES128-GCM-SHA256",
        ssl_protocol="TLSv1.2",
        target_group_arn="arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067",
        trace_id="Root=1-58337327-72bd00b0343d75b906739c42",
        domain_name=None,
        chosen_cert_arn=None,
        matched_rule_priority=1,
        request_creation_time=datetime.datetime(
            2018, 7, 2, 22, 22, 48, 364000, tzinfo=datetime.timezone.utc
        ),
        actions_executed=["redirect"],
        redirect_url="https://example.com:80/",
        error_reason=None,
    )


def test_loadbalancer_http2_entry_auth_error(loadbalancer_http2_entry_auth_error):
    entry = parse_entry(loadbalancer_http2_entry_auth_error, LogType.LoadBalancer)
    assert entry == LoadBalancerLogEntry(
        type=HttpType.H2,
        timestamp=datetime.datetime(
            2018, 7, 2, 22, 23, 0, 186641, tzinfo=datetime.timezone.utc
        ),
        elb="app/my-loadbalancer/50dc6c495c0c9188",
        client=Host(
            ip="192.168.131.39",
            port=2817,
        ),
        target=None,
        request_processing_time=-1.0,
        target_processing_time=-1.0,
        response_processing_time=-1.0,
        elb_status_code=401,
        target_status_code=None,
        received_bytes=4956,
        sent_bytes=616,
        http_request=HttpRequest(
            method="GET",
            url="https://example.com:443/oauth2/idpresponse?code=XXXXX",
            path="/oauth2/idpresponse",
            query={"code": ["XXXXX"]},
            protocol="HTTP/2.0",
        ),
        user_agent="curl/7.46.0",
        ssl_cipher="TLS_AES_128_GCM_SHA256",
        ssl_protocol="TLSv1.3",
        target_group_arn=None,
        trace_id="Root=1-665d7a41-032e7e1d59b8e8043f88b4dc",
        domain_name="example.com",
        chosen_cert_arn="arn:aws:acm:us-east-2:123456789012:certificate/12345678-1234-1234-1234-123456789012",
        matched_rule_priority=-1,
        request_creation_time=datetime.datetime(
            2018, 7, 2, 22, 22, 48, 364000, tzinfo=datetime.timezone.utc
        ),
        actions_executed=["authenticate"],
        redirect_url=None,
        error_reason=LoadBalancerErrorReason.AuthInvalidAWSALBAuthNonce,
    )


def test_loadbalancer_http2_entry_auth_missing(loadbalancer_http2_entry_auth_missing):
    entry = parse_entry(loadbalancer_http2_entry_auth_missing, LogType.LoadBalancer)
    assert entry == LoadBalancerLogEntry(
        type=HttpType.H2,
        timestamp=datetime.datetime(
            2018, 7, 2, 22, 23, 0, 186641, tzinfo=datetime.timezone.utc
        ),
        elb="app/my-loadbalancer/50dc6c495c0c9188",
        client=Host(
            ip="192.168.131.39",
            port=2817,
        ),
        target=None,
        request_processing_time=-1.0,
        target_processing_time=-1.0,
        response_processing_time=-1.0,
        elb_status_code=401,
        target_status_code=None,
        received_bytes=4956,
        sent_bytes=616,
        http_request=HttpRequest(
            method="GET",
            url="https://example.com:443/oauth2/idpresponse?code=XXXXX",
            path="/oauth2/idpresponse",
            query={"code": ["XXXXX"]},
            protocol="HTTP/2.0",
        ),
        user_agent="curl/7.46.0",
        ssl_cipher="TLS_AES_128_GCM_SHA256",
        ssl_protocol="TLSv1.3",
        target_group_arn=None,
        trace_id="Root=1-665d7a41-032e7e1d59b8e8043f88b4dc",
        domain_name="example.com",
        chosen_cert_arn="arn:aws:acm:us-east-2:123456789012:certificate/12345678-1234-1234-1234-123456789012",
        matched_rule_priority=-1,
        request_creation_time=datetime.datetime(
            2018, 7, 2, 22, 22, 48, 364000, tzinfo=datetime.timezone.utc
        ),
        actions_executed=["authenticate"],
        redirect_url=None,
        error_reason=LoadBalancerErrorReason.AuthMissingAWSALBAuthNonce,
    )


def test_loadbalancer_websockets_entry(loadbalancer_websockets_entry):
    entry = parse_entry(loadbalancer_websockets_entry, LogType.LoadBalancer)
    assert entry == LoadBalancerLogEntry(
        type=HttpType.WebSocket,
        timestamp=datetime.datetime(
            2018, 7, 2, 22, 23, 0, 186641, tzinfo=datetime.timezone.utc
        ),
        elb="app/my-loadbalancer/50dc6c495c0c9188",
        client=Host(
            ip="10.0.0.140",
            port=40914,
        ),
        target=Host(
            ip="10.0.1.192",
            port=8010,
        ),
        request_processing_time=0.001,
        target_processing_time=0.003,
        response_processing_time=0.0,
        elb_status_code=101,
        target_status_code=101,
        received_bytes=218,
        sent_bytes=587,
        http_request=HttpRequest(
            method="GET",
            url="http://10.0.0.30:80/",
            path="/",
            query={},
            protocol="HTTP/1.1",
        ),
        user_agent=None,
        ssl_cipher=None,
        ssl_protocol=None,
        target_group_arn="arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067",
        trace_id="Root=1-58337364-23a8c76965a2ef7629b185e3",
        domain_name=None,
        chosen_cert_arn=None,
        matched_rule_priority=1,
        request_creation_time=datetime.datetime(
            2018, 7, 2, 22, 22, 48, 364000, tzinfo=datetime.timezone.utc
        ),
        actions_executed=["forward"],
        redirect_url=None,
        error_reason=None,
    )


def test_loadbalancer_secured_websockets_entry(loadbalancer_secured_websockets_entry):
    entry = parse_entry(loadbalancer_secured_websockets_entry, LogType.LoadBalancer)
    assert entry == LoadBalancerLogEntry(
        type=HttpType.WebSocketSecure,
        timestamp=datetime.datetime(
            2018, 7, 2, 22, 23, 0, 186641, tzinfo=datetime.timezone.utc
        ),
        elb="app/my-loadbalancer/50dc6c495c0c9188",
        client=Host(
            ip="10.0.0.140",
            port=44244,
        ),
        target=Host(
            ip="10.0.0.171",
            port=8010,
        ),
        request_processing_time=0.0,
        target_processing_time=0.001,
        response_processing_time=0.0,
        elb_status_code=101,
        target_status_code=101,
        received_bytes=218,
        sent_bytes=786,
        http_request=HttpRequest(
            method="GET",
            url="https://10.0.0.30:443/",
            path="/",
            query={},
            protocol="HTTP/1.1",
        ),
        user_agent=None,
        ssl_cipher="ECDHE-RSA-AES128-GCM-SHA256",
        ssl_protocol="TLSv1.2",
        target_group_arn="arn:aws:elasticloadbalancing:us-west-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067",
        trace_id="Root=1-58337364-23a8c76965a2ef7629b185e3",
        domain_name=None,
        chosen_cert_arn=None,
        matched_rule_priority=1,
        request_creation_time=datetime.datetime(
            2018, 7, 2, 22, 22, 48, 364000, tzinfo=datetime.timezone.utc
        ),
        actions_executed=["forward"],
        redirect_url=None,
        error_reason=None,
    )


def test_loadbalancer_lambda_entry(loadbalancer_lambda_entry):
    entry = parse_entry(loadbalancer_lambda_entry, LogType.LoadBalancer)
    assert entry == LoadBalancerLogEntry(
        type=HttpType.Http,
        timestamp=datetime.datetime(
            2018, 11, 30, 22, 23, 0, 186641, tzinfo=datetime.timezone.utc
        ),
        elb="app/my-loadbalancer/50dc6c495c0c9188",
        client=Host(
            ip="192.168.131.39",
            port=2817,
        ),
        target=None,
        request_processing_time=0.0,
        target_processing_time=0.001,
        response_processing_time=0.0,
        elb_status_code=200,
        target_status_code=200,
        received_bytes=34,
        sent_bytes=366,
        http_request=HttpRequest(
            method="GET",
            url="http://www.example.com:80/",
            path="/",
            query={},
            protocol="HTTP/1.1",
        ),
        user_agent="curl/7.46.0",
        ssl_cipher=None,
        ssl_protocol=None,
        target_group_arn="arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067",
        trace_id="Root=1-58337364-23a8c76965a2ef7629b185e3",
        domain_name=None,
        chosen_cert_arn=None,
        matched_rule_priority=0,
        request_creation_time=datetime.datetime(
            2018, 11, 30, 22, 22, 48, 364000, tzinfo=datetime.timezone.utc
        ),
        actions_executed=["forward"],
        redirect_url=None,
        error_reason=None,
    )


def test_loadbalancer_lambda_failed_entry(loadbalancer_lambda_failed_entry):
    entry = parse_entry(loadbalancer_lambda_failed_entry, LogType.LoadBalancer)
    assert entry == LoadBalancerLogEntry(
        type=HttpType.Http,
        timestamp=datetime.datetime(
            2018, 11, 30, 22, 23, 0, 186641, tzinfo=datetime.timezone.utc
        ),
        elb="app/my-loadbalancer/50dc6c495c0c9188",
        client=Host(
            ip="192.168.131.39",
            port=2817,
        ),
        target=None,
        request_processing_time=0.0,
        target_processing_time=0.001,
        response_processing_time=0.0,
        elb_status_code=502,
        target_status_code=None,
        received_bytes=34,
        sent_bytes=366,
        http_request=HttpRequest(
            method="GET",
            url="http://www.example.com:80/",
            path="/",
            query={},
            protocol="HTTP/1.1",
        ),
        user_agent="curl/7.46.0",
        ssl_cipher=None,
        ssl_protocol=None,
        target_group_arn="arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067",
        trace_id="Root=1-58337364-23a8c76965a2ef7629b185e3",
        domain_name=None,
        chosen_cert_arn=None,
        matched_rule_priority=0,
        request_creation_time=datetime.datetime(
            2018, 11, 30, 22, 22, 48, 364000, tzinfo=datetime.timezone.utc
        ),
        actions_executed=["forward"],
        redirect_url=None,
        error_reason=LoadBalancerErrorReason.LambdaInvalidResponse,
    )


def test_classic_loadbalancer_http_entry(classic_loadbalancer_http_entry):
    entry = parse_entry(classic_loadbalancer_http_entry, LogType.ClassicLoadBalancer)
    assert entry == ClassicLoadBalancerLogEntry(
        timestamp=datetime.datetime(
            2015, 5, 13, 23, 39, 43, 945958, tzinfo=datetime.timezone.utc
        ),
        elb="my-loadbalancer",
        client=Host(ip="192.168.131.39", port=2817),
        target=Host(ip="10.0.0.1", port=80),
        request_processing_time=0.000086,
        target_processing_time=0.001048,
        response_processing_time=0.001337,
        elb_status_code=200,
        target_status_code=200,
        received_bytes=0,
        sent_bytes=57,
        http_request=HttpRequest(
            method="GET",
            url="https://www.example.com:443/",
            path="/",
            query={},
            protocol="HTTP/1.1",
        ),
        user_agent="curl/7.38.0",
        ssl_cipher="DHE-RSA-AES128-SHA",
        ssl_protocol="TLSv1.2",
    )
