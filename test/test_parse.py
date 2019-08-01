import datetime

from aws_log_parser.fields import (
    CookieField,
    DateField,
    DateTimeField,
    FloatField,
    HostField,
    HttpRequestField,
    HttpTypeField,
    IntegerField,
    IpAddressField,
    ListField,
    LoadBalancerErrorReasonField,
    StringField,
    TimeField,
    UrlQueryField,
    UserAgentField
)
from aws_log_parser.models import (  # CloudFrontRTMPDistributionLogEntry,
    CloudFrontWebDistributionLogEntry,
    LoadBalancerLogEntry,
    LogType
)
from aws_log_parser.parser import log_parser


def parse_entry(contents, log_type):
    return list(log_parser(contents, log_type))[0]


def test_loadbalancer_cloudfront_forward_h2(loadbalancer_cloudfront_forward_h2):
    entry = parse_entry(loadbalancer_cloudfront_forward_h2, LogType.LoadBalancer)
    assert entry == LoadBalancerLogEntry(
        http_type=HttpTypeField('h2'),
        timestamp=DateTimeField('2018-11-30T22:23:00.186641Z'),
        elb=StringField('app/my-loadbalancer/50dc6c495c0c9188'),
        client=HostField('192.168.131.39:2817'),
        target=None,
        request_processing_time=FloatField('0.000'),
        target_processing_time=FloatField('0.001'),
        response_processing_time=FloatField('0.000'),
        elb_status_code=IntegerField('502'),
        target_status_code=None,
        received_bytes=IntegerField('34'),
        sent_bytes=IntegerField('366'),
        http_request=HttpRequestField('GET http://www.example.com:80/ HTTP/1.1'),
        user_agent=UserAgentField('curl/7.46.0'),
        ssl_cipher=None,
        ssl_protocol=None,
        target_group_arn=StringField('arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067'),
        trace_id=StringField('Root=1-58337364-23a8c76965a2ef7629b185e3'),
        domain_name=StringField('api.example.com'),
        chosen_cert_arn=None,
        matched_rule_priority=IntegerField('0'),
        request_creation_time=DateTimeField('2018-11-30T22:22:48.364000Z'),
        actions_executed=ListField('waf,forward'),
        redirect_url=None,
        error_reason=None,
    )


def test_loadbalancer_cloudfront_forward(loadbalancer_cloudfront_forward):
    entry = parse_entry(loadbalancer_cloudfront_forward, LogType.LoadBalancer)
    assert entry == LoadBalancerLogEntry(
        http_type=HttpTypeField('http'),
        timestamp=DateTimeField('2018-11-30T22:23:00.186641Z'),
        elb=StringField('app/my-loadbalancer/50dc6c495c0c9188'),
        client=HostField('192.168.131.39:2817'),
        target=None,
        request_processing_time=FloatField('0.000'),
        target_processing_time=FloatField('0.001'),
        response_processing_time=FloatField('0.000'),
        elb_status_code=IntegerField('502'),
        target_status_code=None,
        received_bytes=IntegerField('34'),
        sent_bytes=IntegerField('366'),
        http_request=HttpRequestField('GET http://www.example.com:80/ HTTP/1.1'),
        user_agent=UserAgentField('curl/7.46.0'),
        ssl_cipher=None,
        ssl_protocol=None,
        target_group_arn=StringField('arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067'),
        trace_id=StringField('Root=1-58337364-23a8c76965a2ef7629b185e3'),
        domain_name=None,
        chosen_cert_arn=None,
        matched_rule_priority=IntegerField('0'),
        request_creation_time=DateTimeField('2018-11-30T22:22:48.364000Z'),
        actions_executed=ListField('waf,forward'),
        redirect_url=None,
        error_reason=None,
    )


def test_loadbalancer_cloudfront_forward_refused(loadbalancer_cloudfront_forward_refused):
    entry = parse_entry(loadbalancer_cloudfront_forward_refused, LogType.LoadBalancer)
    assert entry == LoadBalancerLogEntry(
        http_type=HttpTypeField(raw_value='http'),
        timestamp=DateTimeField(raw_value='2018-11-30T22:23:00.186641Z'),
        elb=StringField(raw_value='app/my-loadbalancer/50dc6c495c0c9188'),
        client=HostField(raw_value='192.168.131.39:2817'),
        target=None,
        request_processing_time=FloatField(raw_value='0.000'),
        target_processing_time=FloatField(raw_value='0.001'),
        response_processing_time=FloatField(raw_value='0.000'),
        elb_status_code=IntegerField(raw_value='502'),
        target_status_code=None,
        received_bytes=IntegerField(raw_value='34'),
        sent_bytes=IntegerField(raw_value='366'),
        http_request=HttpRequestField(raw_value='GET http://www.example.com:80/ HTTP/1.1'),
        user_agent=UserAgentField(raw_value='curl/7.46.0'),
        ssl_cipher=None,
        ssl_protocol=None,
        target_group_arn=StringField(raw_value='arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067'),
        trace_id=StringField(raw_value='Root=1-58337364-23a8c76965a2ef7629b185e3'),
        domain_name=StringField(raw_value='api.example.com'),
        chosen_cert_arn=StringField(raw_value='session-reused'),
        matched_rule_priority=IntegerField(raw_value='0'),
        request_creation_time=DateTimeField(raw_value='2018-11-30T22:22:48.364000Z'),
        actions_executed=ListField(raw_value='waf,forward'),
        redirect_url=None,
        error_reason=None,
    )


def test_cloudfront_entry(cloudfront_entry, cookie_zip_code):
    entry = parse_entry(cloudfront_entry, LogType.CloudFront)
    assert entry == CloudFrontWebDistributionLogEntry(
        date=DateField(raw_value='2014-05-23'),
        time=TimeField(raw_value='01:13:11'),
        edge_location=StringField(raw_value='FRA2'),
        sent_bytes=IntegerField(raw_value='182'),
        client_ip=IpAddressField(raw_value='192.0.2.10'),
        http_method=StringField(raw_value='GET'),
        host=StringField(raw_value='d111111abcdef8.cloudfront.net'),
        uri=StringField(raw_value='/view/my/file.html'),
        status_code=IntegerField(raw_value='200'),
        referrer=StringField(raw_value='www.displaymyfiles.com'),
        user_agent=UserAgentField(raw_value='Mozilla/4.0%20(compatible;%20MSIE%205.0b1;%20Mac_PowerPC)'),
        uri_query=None,
        cookie=CookieField(raw_value='zip=98101'),
        edge_result_type=StringField(raw_value='RefreshHit'),
        edge_request_id=StringField(raw_value='MRVMF7KydIvxMWfJIglgwHQwZsbG2IhRJ07sn9AkKUFSHS9EXAMPLE=='),
        host_header=StringField(raw_value='d111111abcdef8.cloudfront.net'),
        protocol=StringField(raw_value='http'),
        received_bytes=None,
        time_taken=FloatField(raw_value='0.001'),
        forwarded_for=None,
        ssl_protocol=None,
        ssl_cipher=None,
        edge_response_result_type=StringField(raw_value='RefreshHit'),
        protocol_version=StringField(raw_value='HTTP/1.1'),
        fle_encrypted_fields='',
    )
    assert isinstance(entry.timestamp, datetime.datetime) is True
    assert entry.timestamp == datetime.datetime(2014, 5, 23, 1, 13, 11, tzinfo=datetime.timezone.utc)


def test_cloudfront_entry_broken_cookie(cloudfront_entry_broken_cookie, cookie_empty):
    entry = parse_entry(cloudfront_entry_broken_cookie, LogType.CloudFront)
    assert entry == CloudFrontWebDistributionLogEntry(
        date=DateField(raw_value='2014-05-23'),
        time=TimeField(raw_value='01:13:11'),
        edge_location=StringField(raw_value='FRA2'),
        sent_bytes=IntegerField(raw_value='182'),
        client_ip=IpAddressField(raw_value='192.0.2.10'),
        http_method=StringField(raw_value='GET'),
        host=StringField(raw_value='d111111abcdef8.cloudfront.net'),
        uri=StringField(raw_value='/view/my/file.html'),
        status_code=IntegerField(raw_value='200'),
        referrer=StringField(raw_value='www.displaymyfiles.com'),
        user_agent=UserAgentField(raw_value='Mozilla/4.0%20(compatible;%20MSIE%205.0b1;%20Mac_PowerPC)'),
        uri_query=None,
        cookie=CookieField(raw_value='zip 98101'),
        edge_result_type=StringField(raw_value='RefreshHit'),
        edge_request_id=StringField(raw_value='MRVMF7KydIvxMWfJIglgwHQwZsbG2IhRJ07sn9AkKUFSHS9EXAMPLE=='),
        host_header=StringField(raw_value='d111111abcdef8.cloudfront.net'),
        protocol=StringField(raw_value='http'),
        received_bytes=None,
        time_taken=FloatField(raw_value='0.001'),
        forwarded_for=None,
        ssl_protocol=None,
        ssl_cipher=None,
        edge_response_result_type=StringField(raw_value='RefreshHit'),
        protocol_version=StringField(raw_value='HTTP/1.1'),
        fle_encrypted_fields='',
    )
    assert isinstance(entry.timestamp, datetime.datetime) is True
    assert entry.timestamp == datetime.datetime(2014, 5, 23, 1, 13, 11, tzinfo=datetime.timezone.utc)


def test_cloudfront_entry2(cloudfront_entry2, cookie_zip_code):
    entry = parse_entry(cloudfront_entry2, LogType.CloudFront)
    assert entry == CloudFrontWebDistributionLogEntry(
        date=DateField(raw_value='2014-05-23'),
        time=TimeField(raw_value='01:13:12'),
        edge_location=StringField(raw_value='LAX1'),
        sent_bytes=IntegerField(raw_value='2390282'),
        client_ip=IpAddressField(raw_value='192.0.2.202'),
        http_method=StringField(raw_value='GET'),
        host=StringField(raw_value='d111111abcdef8.cloudfront.net'),
        uri=StringField(raw_value='/soundtrack/happy.mp3'),
        status_code=IntegerField(raw_value='304'),
        referrer=StringField(raw_value='www.unknownsingers.com'),
        user_agent=UserAgentField(raw_value='Mozilla/4.0%20(compatible;%20MSIE%207.0;%20Windows%20NT%205.1)'),
        uri_query=UrlQueryField(raw_value='a=b&c=d'),
        cookie=CookieField(raw_value='zip=98101'),
        edge_result_type=StringField(raw_value='Hit'),
        edge_request_id=StringField(raw_value='xGN7KWpVEmB9Dp7ctcVFQC4E-nrcOcEKS3QyAez--06dV7TEXAMPLE=='),
        host_header=StringField(raw_value='d111111abcdef8.cloudfront.net'),
        protocol=StringField(raw_value='http'),
        received_bytes=None,
        time_taken=FloatField(raw_value='0.002'),
        forwarded_for=None,
        ssl_protocol=None,
        ssl_cipher=None,
        edge_response_result_type=StringField(raw_value='Hit'),
        protocol_version=StringField(raw_value='HTTP/1.1'),
        fle_encrypted_fields='',
    )


def test_loadbalancer_http_entry(loadbalancer_http_entry):
    entry = parse_entry(loadbalancer_http_entry, LogType.LoadBalancer)
    assert entry == LoadBalancerLogEntry(
        http_type=HttpTypeField(raw_value='http'),
        timestamp=DateTimeField(raw_value='2018-07-02T22:23:00.186641Z'),
        elb=StringField(raw_value='app/my-loadbalancer/50dc6c495c0c9188'),
        client=HostField(raw_value='192.168.131.39:2817'),
        target=HostField(raw_value='10.0.0.1:80'),
        request_processing_time=FloatField(raw_value='0.000'),
        target_processing_time=FloatField(raw_value='0.001'),
        response_processing_time=FloatField(raw_value='0.000'),
        elb_status_code=IntegerField(raw_value='200'),
        target_status_code=IntegerField(raw_value='200'),
        received_bytes=IntegerField(raw_value='34'),
        sent_bytes=IntegerField(raw_value='366'),
        http_request=HttpRequestField(raw_value='GET http://www.example.com:80/?a=b&c=d&zip=98101 HTTP/1.1'),
        user_agent=UserAgentField(raw_value='curl/7.46.0'),
        ssl_cipher=None,
        ssl_protocol=None,
        target_group_arn=StringField(raw_value='arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067'),
        trace_id=StringField(raw_value='Root=1-58337262-36d228ad5d99923122bbe354'),
        domain_name=None,
        chosen_cert_arn=None,
        matched_rule_priority=IntegerField(raw_value='0'),
        request_creation_time=DateTimeField(raw_value='2018-07-02T22:22:48.364000Z'),
        actions_executed=ListField(raw_value='forward'),
        redirect_url=None,
        error_reason=None,
    )


def test_loadbalancer_https_entry(loadbalancer_https_entry):
    entry = parse_entry(loadbalancer_https_entry, LogType.LoadBalancer)
    assert entry == LoadBalancerLogEntry(
        http_type=HttpTypeField(raw_value='https'),
        timestamp=DateTimeField(raw_value='2018-07-02T22:23:00.186641Z'),
        elb=StringField(raw_value='app/my-loadbalancer/50dc6c495c0c9188'),
        client=HostField(raw_value='192.168.131.39:2817'),
        target=HostField(raw_value='10.0.0.1:80'),
        request_processing_time=FloatField(raw_value='0.086'),
        target_processing_time=FloatField(raw_value='0.048'),
        response_processing_time=FloatField(raw_value='0.037'),
        elb_status_code=IntegerField(raw_value='200'),
        target_status_code=IntegerField(raw_value='200'),
        received_bytes=IntegerField(raw_value='0'),
        sent_bytes=IntegerField(raw_value='57'),
        http_request=HttpRequestField(raw_value='GET https://www.example.com:443/ HTTP/1.1'),
        user_agent=UserAgentField(raw_value='curl/7.46.0'),
        ssl_cipher=StringField(raw_value='ECDHE-RSA-AES128-GCM-SHA256'),
        ssl_protocol=StringField(raw_value='TLSv1.2'),
        target_group_arn=StringField(raw_value='arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067'),
        trace_id=StringField(raw_value='Root=1-58337281-1d84f3d73c47ec4e58577259'),
        domain_name=StringField(raw_value='www.example.com'),
        chosen_cert_arn=StringField(raw_value='arn:aws:acm:us-east-2:123456789012:certificate/12345678-1234-1234-1234-123456789012'),
        matched_rule_priority=IntegerField(raw_value='1'),
        request_creation_time=DateTimeField(raw_value='2018-07-02T22:22:48.364000Z'),
        actions_executed=ListField(raw_value='authenticate,forward'),
        redirect_url=None,
        error_reason=None,
    )


def test_loadbalancer_http2_entry(loadbalancer_http2_entry):
    entry = parse_entry(loadbalancer_http2_entry, LogType.LoadBalancer)
    assert entry == LoadBalancerLogEntry(
        http_type=HttpTypeField(raw_value='h2'),
        timestamp=DateTimeField(raw_value='2018-07-02T22:23:00.186641Z'),
        elb=StringField(raw_value='app/my-loadbalancer/50dc6c495c0c9188'),
        client=HostField(raw_value='10.0.1.252:48160'),
        target=HostField(raw_value='10.0.0.66:9000'),
        request_processing_time=FloatField(raw_value='0.000'),
        target_processing_time=FloatField(raw_value='0.002'),
        response_processing_time=FloatField(raw_value='0.000'),
        elb_status_code=IntegerField(raw_value='200'),
        target_status_code=IntegerField(raw_value='200'),
        received_bytes=IntegerField(raw_value='5'),
        sent_bytes=IntegerField(raw_value='257'),
        http_request=HttpRequestField(raw_value='GET https://10.0.2.105:773/ HTTP/2.0'),
        user_agent=UserAgentField(raw_value='curl/7.46.0'),
        ssl_cipher=StringField(raw_value='ECDHE-RSA-AES128-GCM-SHA256'),
        ssl_protocol=StringField(raw_value='TLSv1.2'),
        target_group_arn=StringField(raw_value='arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067'),
        trace_id=StringField(raw_value='Root=1-58337327-72bd00b0343d75b906739c42'),
        domain_name=None,
        chosen_cert_arn=None,
        matched_rule_priority=IntegerField(raw_value='1'),
        request_creation_time=DateTimeField(raw_value='2018-07-02T22:22:48.364000Z'),
        actions_executed=ListField(raw_value='redirect'),
        redirect_url=StringField(raw_value='https://example.com:80/'),
        error_reason=None,
    )


def test_loadbalancer_websockets_entry(loadbalancer_websockets_entry):
    entry = parse_entry(loadbalancer_websockets_entry, LogType.LoadBalancer)
    assert entry == LoadBalancerLogEntry(
        http_type=HttpTypeField(raw_value='ws'),
        timestamp=DateTimeField(raw_value='2018-07-02T22:23:00.186641Z'),
        elb=StringField(raw_value='app/my-loadbalancer/50dc6c495c0c9188'),
        client=HostField(raw_value='10.0.0.140:40914'),
        target=HostField(raw_value='10.0.1.192:8010'),
        request_processing_time=FloatField(raw_value='0.001'),
        target_processing_time=FloatField(raw_value='0.003'),
        response_processing_time=FloatField(raw_value='0.000'),
        elb_status_code=IntegerField(raw_value='101'),
        target_status_code=IntegerField(raw_value='101'),
        received_bytes=IntegerField(raw_value='218'),
        sent_bytes=IntegerField(raw_value='587'),
        http_request=HttpRequestField(raw_value='GET http://10.0.0.30:80/ HTTP/1.1'),
        user_agent=None,
        ssl_cipher=None,
        ssl_protocol=None,
        target_group_arn=StringField(raw_value='arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067'),
        trace_id=StringField(raw_value='Root=1-58337364-23a8c76965a2ef7629b185e3'),
        domain_name=None,
        chosen_cert_arn=None,
        matched_rule_priority=IntegerField(raw_value='1'),
        request_creation_time=DateTimeField(raw_value='2018-07-02T22:22:48.364000Z'),
        actions_executed=ListField(raw_value='forward'),
        redirect_url=None,
        error_reason=None,
    )


def test_loadbalancer_secured_websockets_entry(loadbalancer_secured_websockets_entry):
    entry = parse_entry(loadbalancer_secured_websockets_entry, LogType.LoadBalancer)
    assert entry == LoadBalancerLogEntry(
        http_type=HttpTypeField(raw_value='wss'),
        timestamp=DateTimeField(raw_value='2018-07-02T22:23:00.186641Z'),
        elb=StringField(raw_value='app/my-loadbalancer/50dc6c495c0c9188'),
        client=HostField(raw_value='10.0.0.140:44244'),
        target=HostField(raw_value='10.0.0.171:8010'),
        request_processing_time=FloatField(raw_value='0.000'),
        target_processing_time=FloatField(raw_value='0.001'),
        response_processing_time=FloatField(raw_value='0.000'),
        elb_status_code=IntegerField(raw_value='101'),
        target_status_code=IntegerField(raw_value='101'),
        received_bytes=IntegerField(raw_value='218'),
        sent_bytes=IntegerField(raw_value='786'),
        http_request=HttpRequestField(raw_value='GET https://10.0.0.30:443/ HTTP/1.1'),
        user_agent=None,
        ssl_cipher=StringField(raw_value='ECDHE-RSA-AES128-GCM-SHA256'),
        ssl_protocol=StringField(raw_value='TLSv1.2'),
        target_group_arn=StringField(raw_value='arn:aws:elasticloadbalancing:us-west-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067'),
        trace_id=StringField(raw_value='Root=1-58337364-23a8c76965a2ef7629b185e3'),
        domain_name=None,
        chosen_cert_arn=None,
        matched_rule_priority=IntegerField(raw_value='1'),
        request_creation_time=DateTimeField(raw_value='2018-07-02T22:22:48.364000Z'),
        actions_executed=ListField(raw_value='forward'),
        redirect_url=None,
        error_reason=None,
    )


def test_loadbalancer_lambda_entry(loadbalancer_lambda_entry):
    entry = parse_entry(loadbalancer_lambda_entry, LogType.LoadBalancer)
    assert entry == LoadBalancerLogEntry(
        http_type=HttpTypeField(raw_value='http'),
        timestamp=DateTimeField(raw_value='2018-11-30T22:23:00.186641Z'),
        elb=StringField(raw_value='app/my-loadbalancer/50dc6c495c0c9188'),
        client=HostField(raw_value='192.168.131.39:2817'),
        target=None,
        request_processing_time=FloatField(raw_value='0.000'),
        target_processing_time=FloatField(raw_value='0.001'),
        response_processing_time=FloatField(raw_value='0.000'),
        elb_status_code=IntegerField(raw_value='200'),
        target_status_code=IntegerField(raw_value='200'),
        received_bytes=IntegerField(raw_value='34'),
        sent_bytes=IntegerField(raw_value='366'),
        http_request=HttpRequestField(raw_value='GET http://www.example.com:80/ HTTP/1.1'),
        user_agent=UserAgentField(raw_value='curl/7.46.0'),
        ssl_cipher=None,
        ssl_protocol=None,
        target_group_arn=StringField(raw_value='arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067'),
        trace_id=StringField(raw_value='Root=1-58337364-23a8c76965a2ef7629b185e3'),
        domain_name=None,
        chosen_cert_arn=None,
        matched_rule_priority=IntegerField(raw_value='0'),
        request_creation_time=DateTimeField(raw_value='2018-11-30T22:22:48.364000Z'),
        actions_executed=ListField(raw_value='forward'),
        redirect_url=None,
        error_reason=None,
    )


def test_loadbalancer_lambda_failed_entry(loadbalancer_lambda_failed_entry):
    entry = parse_entry(loadbalancer_lambda_failed_entry, LogType.LoadBalancer)
    assert entry == LoadBalancerLogEntry(
        http_type=HttpTypeField(raw_value='http'),
        timestamp=DateTimeField(raw_value='2018-11-30T22:23:00.186641Z'),
        elb=StringField(raw_value='app/my-loadbalancer/50dc6c495c0c9188'),
        client=HostField(raw_value='192.168.131.39:2817'),
        target=None,
        request_processing_time=FloatField(raw_value='0.000'),
        target_processing_time=FloatField(raw_value='0.001'),
        response_processing_time=FloatField(raw_value='0.000'),
        elb_status_code=IntegerField(raw_value='502'),
        target_status_code=None,
        received_bytes=IntegerField(raw_value='34'),
        sent_bytes=IntegerField(raw_value='366'),
        http_request=HttpRequestField(raw_value='GET http://www.example.com:80/ HTTP/1.1'),
        user_agent=UserAgentField(raw_value='curl/7.46.0'),
        ssl_cipher=None,
        ssl_protocol=None,
        target_group_arn=StringField(raw_value='arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067'),
        trace_id=StringField(raw_value='Root=1-58337364-23a8c76965a2ef7629b185e3'),
        domain_name=None,
        chosen_cert_arn=None,
        matched_rule_priority=IntegerField(raw_value='0'),
        request_creation_time=DateTimeField(raw_value='2018-11-30T22:22:48.364000Z'),
        actions_executed=ListField(raw_value='forward'),
        redirect_url=None,
        error_reason=LoadBalancerErrorReasonField(raw_value='LambdaInvalidResponse'),
    )
