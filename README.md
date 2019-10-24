[![Build Status](https://travis-ci.org/dpetzold/aws-log-parser.svg?branch=master)](https://travis-ci.org/dpetzold/aws-log-parser)
[![Coverage Status](https://coveralls.io/repos/github/dpetzold/aws-log-parser/badge.svg?branch=master)](https://coveralls.io/github/dpetzold/aws-log-parser?branch=master)

# aws-log-parser

Parse AWS LoadBalancer and CloudFront logs into Python3 data classes.

## CloudFront Example

```python
    >>> from aws_log_parser import log_parser, LogType
    >>> entry = log_parser(log_data, LogType.CloudFront)[0]
    >>> entry
    CloudFrontWebDistributionLogEntry(
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
        user_agent=mozilla_user_agent_fixture,
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
    >>> entry.country
    'United States'
    >>> entry.hostname
    'rate-limited-proxy-66-249-91-41.google.com'
    >>> entry.network
    'Google'
```

## LoadBalancer Example

```python
    >>> from aws_log_parser import log_parser, LogType
    >>> entry = log_parser(log_data, LogType.LoadBalancer)[0]
    >>> entry
    LoadBalancerLogEntry(
        http_type=HttpType('h2'),
        timestamp=datetime.datetime(
            2018, 11, 30, 22, 23, 0, 186641, tzinfo=datetime.timezone.utc,
        ),
        elb='app/my-loadbalancer/50dc6c495c0c9188',
        client=Host(ip='66.249.91.41', port=2817),
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
        user_agent=curl_user_agent_fixture,
        ssl_cipher=None,
        ssl_protocol=None,
        target_group_arn='arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067',
        trace_id='Root=1-58337364-23a8c76965a2ef7629b185e3',
        domain_name='api.example.com',
        chosen_cert_arn=None,
        matched_rule_priority=0,
        request_creation_time=datetime.datetime(
            2018, 11, 30, 22, 22, 48, 364000, tzinfo=datetime.timezone.utc,
        ),
        actions_executed=['waf', 'forward'],
        redirect_url=None,
        error_reason=None,
    )
```
