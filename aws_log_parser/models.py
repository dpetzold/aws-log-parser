import datetime
from dataclasses import dataclass
from enum import Enum, auto

from .fields import (
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


class HttpType(Enum):
    Http = 'http'
    Https = 'https'
    H2 = 'h2'
    WebSocket = 'ws'
    WebSocketSecure = 'wss'


@dataclass(frozen=True)
class NormalizedField:
    source_ip: str
    status_code: str
    url_params: dict


class LogEntry:

    @property
    def ip(self):
        return (
            self.client.parsed.ip
            if isinstance(self, LoadBalancerLogEntry) else
            self.client_ip
        )

    """
    def normalize(self):
        if isinstance(self, LoadBalancerLogEntry):
            return NormalizedField(
                source_ip=self.client.ip,
                status_code=self.elb_status_code,
                url_params=self.http_request.query,
            )

        return NormalizedField(
            source_ip=self.client_ip,
            status_code=self.status_code,
            url_params=self.uri_query,
        )
    """


@dataclass(frozen=True)
class Host:
    ip: IpAddressField
    port: IntegerField


@dataclass(frozen=True)
class HttpRequest:
    method: StringField
    url: StringField
    query: UrlQueryField
    protocol: StringField


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
    http_type: HttpTypeField
    timestamp: DateTimeField
    elb: StringField
    client: HostField
    target: HostField
    request_processing_time: FloatField
    target_processing_time: FloatField
    response_processing_time: FloatField
    elb_status_code: IntegerField
    target_status_code: IntegerField
    received_bytes: IntegerField
    sent_bytes: IntegerField
    http_request: HttpRequestField
    user_agent: UserAgentField
    ssl_cipher: StringField
    ssl_protocol: StringField
    target_group_arn: StringField
    trace_id: StringField
    domain_name: StringField
    chosen_cert_arn: StringField
    matched_rule_priority: IntegerField
    request_creation_time: DateTimeField
    actions_executed: ListField
    redirect_url: StringField
    error_reason: LoadBalancerErrorReasonField


@dataclass(frozen=True)
class CloudFrontWebDistributionLogEntry(LogEntry):
    date: DateField
    time: TimeField
    edge_location: StringField
    sent_bytes: IntegerField
    client_ip: IpAddressField
    http_method: StringField
    host: StringField
    uri: StringField
    status_code: IntegerField
    referrer: StringField
    user_agent: UserAgentField
    uri_query: UrlQueryField
    cookie: CookieField
    edge_result_type: StringField
    edge_request_id: StringField
    host_header: StringField
    protocol: StringField
    received_bytes: IntegerField
    time_taken: FloatField
    forwarded_for: StringField  # NOQA: E701 ??
    ssl_protocol: StringField
    ssl_cipher: StringField
    edge_response_result_type: StringField
    protocol_version: StringField
    fle_encrypted_fields: StringField = ''

    @property
    def timestamp(self):
        return datetime.datetime.fromisoformat(
            f'{self.date}T{self.time}',
        ).replace(tzinfo=datetime.timezone.utc)


@dataclass(frozen=True)
class CloudFrontRTMPDistributionLogEntry(LogEntry):
    date: StringField
    time: StringField
    edge_location: StringField
    client_ip: StringField
    event: StringField
    sent_bytes: IntegerField
    status_code: StringField
    client_id: StringField
    uri_stream: StringField
    uri_query: UrlQueryField
    referrer: StringField
    page_url: StringField
    user_agent: UserAgentField


@dataclass(frozen=True)
class LogFormat:
    name: StringField
    model: LogEntry
    delimiter: chr


@dataclass(frozen=True)
class LogType:
    LoadBalancer: LogFormat = LogFormat(
        name='LoadBalancer',
        model=LoadBalancerLogEntry,
        delimiter=' ',
    )

    CloudFront: LogFormat = LogFormat(
        name='CloudFront',
        model=CloudFrontWebDistributionLogEntry,
        delimiter='\t',
    )

    CloudFrontRTMP: LogFormat = LogFormat(
        name='CloudFrontRTMP',
        model=CloudFrontRTMPDistributionLogEntry,
        delimiter='\t',
    )
