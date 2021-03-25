import pytest

from http import cookies
from io import StringIO


def log_entry(entry):
    return StringIO(entry)


@pytest.fixture
def cookie_zip_code():
    cookie = cookies.SimpleCookie()
    cookie.load(rawdata="zip=98101")
    return cookie


@pytest.fixture
def cookie_with_space():
    cookie = cookies.SimpleCookie()
    cookie.load(rawdata="this zip=98101")
    return cookie


@pytest.fixture
def cookie_empty():
    cookie = cookies.SimpleCookie()
    cookie.load(rawdata="")
    return cookie


@pytest.fixture
def cloudfront_entry():
    return log_entry(
        """2014-05-23	01:13:11	FRA2	182	192.0.2.10	GET	d111111abcdef8.cloudfront.net	/view/my/file.html	200	www.displaymyfiles.com	Mozilla/4.0%20(compatible;%20MSIE%205.0b1;%20Mac_PowerPC)	-	zip=98101	RefreshHit	MRVMF7KydIvxMWfJIglgwHQwZsbG2IhRJ07sn9AkKUFSHS9EXAMPLE==	d111111abcdef8.cloudfront.net	http	-	0.001	-	-	-	RefreshHit	HTTP/1.1"""
    )  # noqa: E501


@pytest.fixture
def cloudfront_entry_broken_cookie():
    return log_entry(
        """2014-05-23	01:13:11	FRA2	182	192.0.2.10	GET	d111111abcdef8.cloudfront.net	/view/my/file.html	200	www.displaymyfiles.com	Mozilla/4.0%20(compatible;%20MSIE%205.0b1;%20Mac_PowerPC)	-	zip 98101	RefreshHit	MRVMF7KydIvxMWfJIglgwHQwZsbG2IhRJ07sn9AkKUFSHS9EXAMPLE==	d111111abcdef8.cloudfront.net	http	-	0.001	-	-	-	RefreshHit	HTTP/1.1"""
    )  # noqa: E501


@pytest.fixture
def cloudfront_entry_cookie_with_encoding():
    return log_entry(
        """2014-05-23	01:13:11	FRA2	182	192.0.2.10	GET	d111111abcdef8.cloudfront.net	/view/my/file.html	200	www.displaymyfiles.com	Mozilla/4.0%20(compatible;%20MSIE%205.0b1;%20Mac_PowerPC)	-	this%20zip=98101	RefreshHit	MRVMF7KydIvxMWfJIglgwHQwZsbG2IhRJ07sn9AkKUFSHS9EXAMPLE==	d111111abcdef8.cloudfront.net	http	-	0.001	-	-	-	RefreshHit	HTTP/1.1"""
    )  # noqa: E501


@pytest.fixture
def cloudfront_entry2():
    return log_entry(
        """2014-05-23	01:13:12	LAX1	2390282	192.0.2.202	GET	d111111abcdef8.cloudfront.net	/soundtrack/happy.mp3	304	www.unknownsingers.com	Mozilla/4.0%20(compatible;%20MSIE%207.0;%20Windows%20NT%205.1)	a=b&c=d	zip=98101	Hit	xGN7KWpVEmB9Dp7ctcVFQC4E-nrcOcEKS3QyAez--06dV7TEXAMPLE==	d111111abcdef8.cloudfront.net	http	-	0.002	-	-	-	Hit	HTTP/1.1"""
    )  # noqa: E501


@pytest.fixture
def loadbalancer_http_entry():
    return log_entry(
        '''http 2018-07-02T22:23:00.186641Z app/my-loadbalancer/50dc6c495c0c9188 192.168.131.39:2817 10.0.0.1:80 0.000 0.001 0.000 200 200 34 366 "GET http://www.example.com:80/?a=b&c=d&zip=98101 HTTP/1.1" "curl/7.46.0" - - arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067 "Root=1-58337262-36d228ad5d99923122bbe354" "-" "-" 0 2018-07-02T22:22:48.364000Z "forward" "-" "-"'''
    )  # noqa: E501


@pytest.fixture
def loadbalancer_https_entry():
    return log_entry(
        '''https 2018-07-02T22:23:00.186641Z app/my-loadbalancer/50dc6c495c0c9188 192.168.131.39:2817 10.0.0.1:80 0.086 0.048 0.037 200 200 0 57 "GET https://www.example.com:443/ HTTP/1.1" "curl/7.46.0" ECDHE-RSA-AES128-GCM-SHA256 TLSv1.2 arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067 "Root=1-58337281-1d84f3d73c47ec4e58577259" "www.example.com" "arn:aws:acm:us-east-2:123456789012:certificate/12345678-1234-1234-1234-123456789012" 1 2018-07-02T22:22:48.364000Z "authenticate,forward" "-" "-"'''
    )  # noqa: E501


@pytest.fixture
def loadbalancer_http2_entry():
    return log_entry(
        '''h2 2018-07-02T22:23:00.186641Z app/my-loadbalancer/50dc6c495c0c9188 10.0.1.252:48160 10.0.0.66:9000 0.000 0.002 0.000 200 200 5 257 "GET https://10.0.2.105:773/ HTTP/2.0" "curl/7.46.0" ECDHE-RSA-AES128-GCM-SHA256 TLSv1.2 arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067 "Root=1-58337327-72bd00b0343d75b906739c42" "-" "-" 1 2018-07-02T22:22:48.364000Z "redirect" "https://example.com:80/" "-"'''
    )  # noqa: E501


@pytest.fixture
def loadbalancer_websockets_entry():
    return log_entry(
        '''ws 2018-07-02T22:23:00.186641Z app/my-loadbalancer/50dc6c495c0c9188 10.0.0.140:40914 10.0.1.192:8010 0.001 0.003 0.000 101 101 218 587 "GET http://10.0.0.30:80/ HTTP/1.1" "-" - - arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067 "Root=1-58337364-23a8c76965a2ef7629b185e3" "-" "-" 1 2018-07-02T22:22:48.364000Z "forward" "-" "-"'''
    )  # noqa: E501


@pytest.fixture
def loadbalancer_secured_websockets_entry():
    return log_entry(
        '''wss 2018-07-02T22:23:00.186641Z app/my-loadbalancer/50dc6c495c0c9188 10.0.0.140:44244 10.0.0.171:8010 0.000 0.001 0.000 101 101 218 786 "GET https://10.0.0.30:443/ HTTP/1.1" "-" ECDHE-RSA-AES128-GCM-SHA256 TLSv1.2 arn:aws:elasticloadbalancing:us-west-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067 "Root=1-58337364-23a8c76965a2ef7629b185e3" "-" "-" 1 2018-07-02T22:22:48.364000Z "forward" "-" "-"'''
    )  # noqa: E501


@pytest.fixture
def loadbalancer_lambda_entry():
    return log_entry(
        '''http 2018-11-30T22:23:00.186641Z app/my-loadbalancer/50dc6c495c0c9188 192.168.131.39:2817 - 0.000 0.001 0.000 200 200 34 366 "GET http://www.example.com:80/ HTTP/1.1" "curl/7.46.0" - - arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067 "Root=1-58337364-23a8c76965a2ef7629b185e3" "-" "-" 0 2018-11-30T22:22:48.364000Z "forward" "-" "-"'''
    )  # noqa: E501


@pytest.fixture
def loadbalancer_lambda_failed_entry():
    return log_entry(
        '''http 2018-11-30T22:23:00.186641Z app/my-loadbalancer/50dc6c495c0c9188 192.168.131.39:2817 - 0.000 0.001 0.000 502 - 34 366 "GET http://www.example.com:80/ HTTP/1.1" "curl/7.46.0" - - arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067 "Root=1-58337364-23a8c76965a2ef7629b185e3" "-" "-" 0 2018-11-30T22:22:48.364000Z "forward" "-" "LambdaInvalidResponse"'''
    )  # noqa: E501


@pytest.fixture
def loadbalancer_cloudfront_forward():
    return log_entry(
        '''http 2018-11-30T22:23:00.186641Z app/my-loadbalancer/50dc6c495c0c9188 192.168.131.39:2817 - 0.000 0.001 0.000 502 - 34 366 "GET http://www.example.com:80/ HTTP/1.1" "curl/7.46.0" - - arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067 "Root=1-58337364-23a8c76965a2ef7629b185e3" "-" "-" 0 2018-11-30T22:22:48.364000Z "waf,forward" "-" "-"'''
    )  # noqa: E501


@pytest.fixture
def loadbalancer_cloudfront_forward_refused():
    return log_entry(
        '''http 2018-11-30T22:23:00.186641Z app/my-loadbalancer/50dc6c495c0c9188 192.168.131.39:2817 - 0.000 0.001 0.000 502 - 34 366 "GET http://www.example.com:80/ HTTP/1.1" "curl/7.46.0" - - arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067 "Root=1-58337364-23a8c76965a2ef7629b185e3" "api.example.com" "session-reused" 0 2018-11-30T22:22:48.364000Z "waf,forward" "-" "-"'''
    )  # noqa: E501


@pytest.fixture
def loadbalancer_cloudfront_forward_h2():
    return log_entry(
        '''h2 2018-11-30T22:23:00.186641Z app/my-loadbalancer/50dc6c495c0c9188 192.168.131.39:2817 - 0.000 0.001 0.000 502 - 34 366 "GET http://www.example.com:80/ HTTP/1.1" "curl/7.46.0" - - arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067 "Root=1-58337364-23a8c76965a2ef7629b185e3" "api.example.com" "-" 0 2018-11-30T22:22:48.364000Z "waf,forward" "-" "-"'''
    )  # noqa: E501


@pytest.fixture
def classic_loadbalancer_http_entry():
    return log_entry(
        """2015-05-13T23:39:43.945958Z my-loadbalancer 192.168.131.39:2817 10.0.0.1:80 0.000086 0.001048 0.001337 200 200 0 57 "GET https://www.example.com:443/ HTTP/1.1" "curl/7.38.0" DHE-RSA-AES128-SHA TLSv1.2"""
    )
