from aws_log_parser.fields import (
    UrlQuotedField,
    UserAgentField,
)


def test_url_quoted_field():

    field = UrlQuotedField('user_agent', '"Mozilla/4.0%20(compatible;%20MSIE%205.0b1;%20Mac_PowerPC)"')
    assert field.value == 'Mozilla/4.0%20(compatible;%20MSIE%205.0b1;%20Mac_PowerPC)'
    assert field.parsed == 'Mozilla/4.0 (compatible; MSIE 5.0b1; Mac_PowerPC)'


def test_user_agent_field():

    # Chrome 63 on iOS 11
    field = UserAgentField('user_agent', '"Mozilla/5.0 (iPhone; CPU iPhone OS 11_0_3 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) CriOS/63.0.3239.73 Mobile/15A432 Safari/604.1"')
    assert field.device_type == 'mobile'
