import datetime
import functools
import ipaddress
import logging
import socket
import urllib.parse
from dataclasses import dataclass
from http import cookies

import geoip2.database
import user_agents

from .exceptions import UnknownHttpType

logger = logging.getLogger(__name__)


try:
    geoip_reader = geoip2.database.Reader('./GeoLite2-Country.mmdb')
except FileNotFoundError as exc:
    logger.warn(str(exc))
    geoip_reader = None


@functools.lru_cache(maxsize=16384)
def resolve_ip(source_ip):
    socket.setdefaulttimeout(.500)
    try:
        return socket.gethostbyaddr(source_ip)[0]
    except (socket.herror, socket.gaierror) as exc:
        logger.error('Unable to resolve {} {}'.format(source_ip, str(exc)))
        return None


@functools.lru_cache(maxsize=16384)
def parse_user_agent(user_agent):
    return user_agents.parse(user_agent)


@dataclass
class LogField:
    raw_value: str

    @property
    def value(self):
        return self.raw_value.rstrip('"').lstrip('"')

    @property
    def parsed(self):
        raise NotImplementedError

    def __str__(self):
        return self.value


@dataclass
class StringField(LogField):

    @property
    def parsed(self):
        return self.value


@dataclass
class IntegerField(LogField):

    @property
    def parsed(self):
        return int(self.value)


@dataclass
class IpAddressField(LogField):

    @property
    def parsed(self):
        return ipaddress.ip_address(self.value)

    @property
    def hostname(self):
        return resolve_ip(self.value)

    @property
    def country(self):
        try:
            match = geoip_reader.country(self.value)
        except geoip2.errors.AddressNotFoundError:
            return None
        return match.country.name


@dataclass
class FloatField(LogField):

    @property
    def parsed(self):
        return float(self.value)


@dataclass
class HttpTypeField(LogField):

    @property
    def parsed(self):
        from .models import HttpType
        for ht in HttpType:
            if self.value == ht.value:
                return ht
        raise UnknownHttpType(self.value)


@dataclass
class DateTimeField(LogField):

    @property
    def parsed(self):
        return datetime.datetime.fromisoformat(
            self.value.rstrip('Z')
        ).replace(tzinfo=datetime.timezone.utc)


@dataclass
class HttpRequestField(LogField):

    @property
    def parsed(self):
        from .models import HttpRequest
        # The url can contain spaces
        split = self.value.split()
        url = ' '.join(split[1:-1])
        parsed = urllib.parse.urlparse(url)
        return HttpRequest(
            split[0],
            url,
            urllib.parse.parse_qs(parsed.query),
            split[-1],
        )


@dataclass
class CookieField(LogField):

    @property
    def parsed(self):
        cookie = cookies.SimpleCookie()
        cookie.load(rawdata=self.value)
        return cookie


@dataclass
class DateField(LogField):

    @property
    def parsed(self):
        return datetime.date.fromisoformat(self.value)


@dataclass
class TimeField(LogField):

    @property
    def parsed(self):
        return datetime.time.fromisoformat(self.value)


@dataclass
class ListField(LogField):

    @property
    def parsed(self):
        return self.value.split(',')


@dataclass
class LoadBalancerErrorReasonField(LogField):

    @property
    def parsed(self):
        from .models import LoadBalancerErrorReason
        return getattr(LoadBalancerErrorReason, self.value)


@dataclass
class HostField(LogField):

    @property
    def parsed(self):
        from .models import Host
        ip, port = self.value.split(':')
        return Host(IpAddressField(ip), IntegerField(int(port)))


@dataclass
class UrlQueryField(LogField):

    @property
    def parsed(self):
        return urllib.parse.parse_qs(self.value)


@dataclass
class UrlQuotedField(LogField):

    @property
    def parsed(self):
        return urllib.parse.unquote(super().value).replace('%20', ' ')


@dataclass
class UserAgentField(UrlQuotedField):

    @property
    def value(self):
        return super().parsed

    @property
    def parsed(self):
        return parse_user_agent(self.value)

    @property
    def device_type(self):

        device_mappings = {
            'is_mobile': 'mobile',
            'is_tablet': 'tablet',
            'is_touch_capable': 'touch',
            'is_pc': 'pc',
            'is_bot': 'bot',
        }

        user_agent = self.parsed
        for attr, device_type in device_mappings.items():
            if getattr(user_agent, attr):
                return device_type
        return 'unknown'
