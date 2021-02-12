[![Build Status](https://travis-ci.org/dpetzold/aws-log-parser.svg?branch=master)](https://travis-ci.org/dpetzold/aws-log-parser)
[![Coverage Status](https://coveralls.io/repos/github/dpetzold/aws-log-parser/badge.svg?branch=master)](https://coveralls.io/github/dpetzold/aws-log-parser?branch=master)

# aws-log-parser

Python module to parse AWS LoadBalancer and CloudFront logs into Python3 data
classes.

## Install

`pip install aws-log-parser`

## Examples

### CloudFront

```python
    >>> from aws_log_parser import log_parser, LogType
    >>> entries = log_parser(log_data, LogType.CloudFront)
    >>> entries[0]
    CloudFrontWebDistributionLogEntry(
        date=datetime.date(2014, 5, 23),
        time=datetime.time(1, 13, 11),
        edge_location='FRA2',
        sent_bytes=182,
        client_ip='192.0.2.10',
        http_method='GET',
        host='d111111abcdef8.cloudfront.net',
        uri_stream='/view/my/file.html',
        status_code=200,
        referrer='www.displaymyfiles.com',
        user_agent='Mozilla/4.0 (compatible; MSIE 5.0b1; Mac_PowerPC)',
        uri_query=None,
        cookie=cookie_fixture,
        edge_result_type='RefreshHit',
        edge_request_id='MRVMF7KydIvxMWfJIglgwHQwZsbG2IhRJ07sn9AkKUFSHS9EXAMPLE==',
        host_header='d111111abcdef8.cloudfront.net',
        protocol='http',
        received_bytes=None,
        time_taken=0.001,
        forwarded_for=None,
        ssl_protocol=None,
        ssl_chipher=None,
        edge_response_result_type='RefreshHit',
        protocol_version='HTTP/1.1',
    )
```

### LoadBalancer

```python
    >>> from aws_log_parser import log_parser, LogType
    >>> entries = log_parser(log_data, LogType.LoadBalancer)
    >>> entries[0]
    LoadBalancerLogEntry(
        type=HttpType.H2,
        timestamp=datetime.datetime(2019, 5, 10, 0, 55, 0, 578958, tzinfo=datetime.timezone.utc),
        elb='app/my-elb/bae6f4bf83cfba2a',
        client=Host(
            ip='73.9.17.165',
            port=55354,
        ),
        target=Host(
            ip='172.18.16.37',
            port=80,
        ),
        request_processing_time=0.001,
        target_processing_time=0.01,
        response_processing_time=0.0,
        elb_status_code=301,
        target_status_code=301,
        received_bytes=287,
        sent_bytes=465,
        http_request=HttpRequest(
            method='GET',
            url='https://example.it:443/l/27uM',
            query={},
            protocol='HTTP/2.0',
        ),
        user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 [FBAN/FBIOS;FBDV/iPhone10,6;FBMD/iPhone;FBSN/iOS;FBSV/12.2;FBSS/3;FBCR/T-Mobile;FBID/phone;FBLC/en_US;FBOP/5]',
        ssl_cipher='ECDHE-RSA-AES128-GCM-SHA256',
        ssl_protocol='TLSv1.2',
        target_group_arn='arn:aws:elasticloadbalancing:us-east-1:12345678900:targetgroup/my-elb/4bbbb73e0d3ddadc',
        trace_id='Root=1-5cd4cbe4-685415e018175510cb4e3588',
        domain_name='example.it',
        chosen_cert_arn='arn:aws:acm:us-east-1:12345678900:certificate/3e6b547b-dd22-41f2-9130-32f2c21f0ca0',
        matched_rule_priority=0,
        request_creation_time=datetime.datetime(2019, 5, 10, 0, 55, 0, 567000, tzinfo=datetime.timezone.utc),
        actions_executed=['waf', 'forward'],
        redirect_url=None,
        error_reason=None,
    )
```

## Development

Run `bootstrap.sh` to create the virtualenv. The tests can be run with `python
setup.py test` or by running `pytest` directly.
