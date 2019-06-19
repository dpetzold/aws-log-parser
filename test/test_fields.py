from aws_log_parser.fields import UrlQuotedField


def test_url_quoted_field():

    field = UrlQuotedField('user_agent', '"Mozilla/4.0%20(compatible;%20MSIE%205.0b1;%20Mac_PowerPC)"')
    assert field.value == 'Mozilla/4.0%20(compatible;%20MSIE%205.0b1;%20Mac_PowerPC)'
    assert field.parsed == 'Mozilla/4.0 (compatible; MSIE 5.0b1; Mac_PowerPC)'
