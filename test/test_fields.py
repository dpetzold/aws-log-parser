import pytest
import ipaddress

from aws_log_parser.models import HttpRequest
from aws_log_parser.fields import (
    geoip_reader,
    FloatField,
    IntegerField,
    IpAddressField,
    HttpRequestField,
    StringField,
    UrlQuotedField,
    UserAgentField,
)


def test_url_quoted_field():
    field = UrlQuotedField('"Mozilla/4.0%20(compatible;%20MSIE%205.0b1;%20Mac_PowerPC)"')
    assert field.value == 'Mozilla/4.0%20(compatible;%20MSIE%205.0b1;%20Mac_PowerPC)'
    assert field.parsed == 'Mozilla/4.0 (compatible; MSIE 5.0b1; Mac_PowerPC)'


def test_user_agent_field():
    # Chrome 63 on iOS 11
    field = UserAgentField('"Mozilla/5.0%20(iPhone; CPU iPhone OS 11_0_3 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) CriOS/63.0.3239.73 Mobile/15A432 Safari/604.1"')
    assert field.value == 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0_3 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) CriOS/63.0.3239.73 Mobile/15A432 Safari/604.1'
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

@pytest.mark.skipif(geoip_reader is None, reason="geoip database is missing")
def test_ip_address_field_country():
    field = IpAddressField('8.8.8.8')
    assert field.country == 'United States'
