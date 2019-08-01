import datetime
import ipaddress

import pytest

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
    UrlQuotedField,
    UserAgentField,
    geoip_reader
)
from aws_log_parser.models import (
    Host,
    HttpRequest,
    HttpType,
    LoadBalancerErrorReason
)


def test_url_quoted_field():
    field = UrlQuotedField('"Mozilla/4.0%20(compatible;%20MSIE%205.0b1;%20Mac_PowerPC)"')
    assert field.value == 'Mozilla/4.0%20(compatible;%20MSIE%205.0b1;%20Mac_PowerPC)'
    assert field.parsed == 'Mozilla/4.0 (compatible; MSIE 5.0b1; Mac_PowerPC)'


def test_user_agent_field():
    # Chrome 63 on iOS 11
    field = UserAgentField('"Mozilla/5.0%20(iPhone; CPU iPhone OS 11_0_3 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) CriOS/63.0.3239.73 Mobile/15A432 Safari/604.1"')  # NOQA: E501
    assert field.value == 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0_3 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) CriOS/63.0.3239.73 Mobile/15A432 Safari/604.1'  # NOQA: E501
    assert field.device_type == 'mobile'


def test_ip_address_field():
    field = IpAddressField('8.8.8.8')
    assert field.parsed == ipaddress.ip_address('8.8.8.8')
    assert field.hostname == 'dns.google'


def test_string_field():
    field = StringField('Root=1-58337364-23a8c76965a2ef7629b185e3')
    assert field.parsed == 'Root=1-58337364-23a8c76965a2ef7629b185e3'


def test_integer_field():
    field = IntegerField('200')
    assert field.parsed == 200


def test_date_field():
    field = DateField('2019-06-05')
    assert field.parsed == datetime.date(2019, 6, 5)


def test_datetime_field():
    field = DateTimeField('2019-06-05T22:13:22.123444Z')
    assert field.parsed == datetime.datetime(2019, 6, 5, 22, 13, 22, 123444, tzinfo=datetime.timezone.utc)


def test_time_field():
    field = TimeField('22:13:22.123444')
    assert field.parsed == datetime.time(22, 13, 22, 123444)


def test_http_type_field():
    field = HttpTypeField('h2')
    assert field.parsed == HttpType.H2


def test_url_query_field():
    field = UrlQueryField('a=1&b=2')
    assert field.parsed == {'a': ['1'], 'b': ['2']}


def test_host_field():
    field = HostField('192.168.131.39:2817')
    assert field.parsed == Host(ip=IpAddressField('192.168.131.39'), port=IntegerField(2817))


def test_float_field():
    field = FloatField('0.200')
    assert field.parsed == 0.200


def test_http_request_field():
    field = HttpRequestField('GET http://www.example.com:80/ HTTP/1.1')
    assert field.parsed == HttpRequest(
        method='GET',
        url='http://www.example.com:80/',
        query={},
        protocol='HTTP/1.1',
    )


def test_loadbalancer_error_reason_field():
    field = LoadBalancerErrorReasonField(raw_value='LambdaInvalidResponse')
    assert field.parsed == LoadBalancerErrorReason.LambdaInvalidResponse


def test_cookie_field(cookie_zip_code):
    field = CookieField(raw_value='zip=98101')
    assert field.parsed == cookie_zip_code


def test_list_field():
    field = ListField('1,2')
    assert field.parsed == ['1', '2']


@pytest.mark.skipif(geoip_reader is None, reason="geoip database is missing")
def test_ip_address_field_country():
    field = IpAddressField('8.8.8.8')
    assert field.country == 'United States'
