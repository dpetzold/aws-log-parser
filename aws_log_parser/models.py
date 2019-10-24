import datetime
import logging
from dataclasses import dataclass
from enum import (
    Enum,
    auto,
)
import typing

import geoip2.database
from user_agents.parsers import UserAgent

from .util import (
    gethostbyaddr,
    query_radb,
)


logger = logging.getLogger(__name__)


try:
    geoip_reader = geoip2.database.Reader('./GeoLite2-Country.mmdb')
except FileNotFoundError as exc:
    logger.warn(str(exc))
    geoip_reader = None


class HttpType(Enum):
    Http = 'http'
    Https = 'https'
    H2 = 'h2'
    WebSocket = 'ws'
    WebSocketSecure = 'wss'


class LogEntry:

    @property
    def ip(self) -> str:
        return (
            self.client.ip
            if isinstance(self, LoadBalancerLogEntry) else
            self.client_ip
        )

    @property
    def hostname(self) -> str:
        return gethostbyaddr(self.ip)

    @property
    def country(self) -> str:
        try:
            match = geoip_reader.country(self.ip)
        except geoip2.errors.AddressNotFoundError:
            return None
        return match.country.name

    @property
    def network(self) -> str:
        query = query_radb(self.ip)
        if query:
            return query.get('descr')
        return None



@dataclass(frozen=True)
class Host:
    ip: str
    port: int


@dataclass(frozen=True)
class HttpRequest:
    method: str
    url: str
    query: dict
    protocol: str


class LoadBalancerErrorReason(Enum):
    AuthInvalidCookie = auto()
    AuthInvalidGrantError = auto()
    AuthInvalidIdToken = auto()
    AuthInvalidStateParam = auto()
    AuthInvalidTokenResponse = auto()
    AuthInvalidUserinfoResponse = auto()
    AuthMissingCodeParam = auto()
    AuthMissingHostHeader = auto()
    AuthMissingStateParam = auto()
    AuthTokenEpRequestFailed = auto()
    AuthTokenEpRequestTimeout = auto()
    AuthUnhandledException = auto()
    AuthUserinfoEpRequestFailed = auto()
    AuthUserinfoEpRequestTimeout = auto()
    AuthUserinfoResponseSizeExceeded = auto()
    LambdaAccessDenied = auto()
    LambdaConnectionTimeout = auto()
    LambdaEC2AccessDeniedException = auto()
    LambdaEC2ThrottledException = auto()
    LambdaEC2UnexpectedException = auto()
    LambdaENILimitReachedException = auto()
    LambdaInvalidResponse = auto()
    LambdaInvalidRuntimeException = auto()
    LambdaInvalidSecurityGroupIDException = auto()
    LambdaInvalidSubnetIDException = auto()
    LambdaInvalidZipFileException = auto()
    LambdaKMSAccessDeniedException = auto()
    LambdaKMSDisabledException = auto()
    LambdaKMSInvalidStateException = auto()
    LambdaKMSNotFoundException = auto()
    LambdaRequestTooLarge = auto()
    LambdaResourceNotFound = auto()
    LambdaResponseTooLarge = auto()
    LambdaServiceException = auto()
    LambdaSubnetIPAddressLimitReachedException = auto()
    LambdaThrottling = auto()
    LambdaUnhandled = auto()


@dataclass(frozen=True)
class LoadBalancerLogEntry(LogEntry):
    http_type: HttpType
    timestamp: datetime.datetime
    elb: str
    client: Host
    target: Host
    request_processing_time: float
    target_processing_time: float
    response_processing_time: float
    elb_status_code: int
    target_status_code: int
    received_bytes: int
    sent_bytes: int
    http_request: HttpRequest
    user_agent: UserAgent
    ssl_cipher: str
    ssl_protocol: str
    target_group_arn: str
    trace_id: str
    domain_name: str
    chosen_cert_arn: str
    matched_rule_priority: int
    request_creation_time: datetime.datetime
    actions_executed: typing.List[str]
    redirect_url: str
    error_reason: LoadBalancerErrorReason


@dataclass(frozen=True)
class CloudFrontWebDistributionLogEntry(LogEntry):
    date: datetime.date
    time: datetime.time
    edge_location: str
    sent_bytes: int
    client_ip: str
    http_method: str
    host: str
    uri: str
    status_code: int
    referrer: str
    user_agent: UserAgent
    uri_query: str
    cookie: str
    edge_result_type: str
    edge_request_id: str
    host_header: str
    protocol: str
    received_bytes: int
    time_taken: float
    forwarded_for: str
    ssl_protocol: str
    ssl_cipher: str
    edge_response_result_type: str
    protocol_version: str
    fle_encrypted_fields: str = ''

    @property
    def timestamp(self):
        return datetime.datetime.fromisoformat(
            f'{self.date}T{self.time}',
        ).replace(tzinfo=datetime.timezone.utc)


@dataclass(frozen=True)
class CloudFrontRTMPDistributionLogEntry(LogEntry):
    date: str
    time: str
    edge_location: str
    client_ip: str
    event: str
    sent_bytes: int
    status_code: str
    client_id: str
    uri_stream: str
    uri_query: str
    referrer: str
    page_url: str
    user_agent: str


@dataclass(frozen=True)
class LogFormat:
    name: str
    model: LogEntry
    delimiter: chr
    ip_field: str


@dataclass(frozen=True)
class LogType:
    LoadBalancer: LogFormat = LogFormat(
        name='LoadBalancer',
        model=LoadBalancerLogEntry,
        delimiter=' ',
        ip_field='client.ip',
    )

    CloudFront: LogFormat = LogFormat(
        name='CloudFront',
        model=CloudFrontWebDistributionLogEntry,
        delimiter='\t',
        ip_field='client_ip',
    )

    CloudFrontRTMP: LogFormat = LogFormat(
        name='CloudFrontRTMP',
        model=CloudFrontRTMPDistributionLogEntry,
        delimiter='\t',
        ip_field='client_ip',
    )
