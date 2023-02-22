import datetime
import typing

from enum import (
    Enum,
    auto,
)

from dataclasses import dataclass
from http import cookies


class HttpType(Enum):
    Grpc = "grpc"
    Grpcs = "grpcs"
    Http = "http"
    Https = "https"
    H2 = "h2"
    WebSocket = "ws"
    WebSocketSecure = "wss"


@dataclass(frozen=True)
class Host:
    ip: str
    port: int


@dataclass(frozen=True)
class HttpRequest:
    method: str
    url: str
    path: str
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


class LogEntry:
    pass


@dataclass
class ClassicLoadBalancerLogEntry(LogEntry):
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
    user_agent: str
    ssl_cipher: str
    ssl_protocol: str

    instance_id: typing.Optional[str] = None

    @property
    def client_ip(self):
        if self.client:
            return self.client.ip


@dataclass
class LoadBalancerLogEntry(LogEntry):
    type: HttpType
    timestamp: datetime.datetime
    elb: str
    client: Host
    target: typing.Optional[Host]
    request_processing_time: float
    target_processing_time: float
    response_processing_time: float
    elb_status_code: int
    target_status_code: typing.Optional[int]
    received_bytes: int
    sent_bytes: int
    http_request: HttpRequest
    user_agent: typing.Optional[str]
    ssl_cipher: typing.Optional[str]
    ssl_protocol: typing.Optional[str]
    target_group_arn: str
    trace_id: str
    domain_name: typing.Optional[str]
    chosen_cert_arn: typing.Optional[str]
    matched_rule_priority: int
    request_creation_time: datetime.datetime
    actions_executed: typing.List[str]
    redirect_url: typing.Optional[str]
    error_reason: typing.Optional[LoadBalancerErrorReason]


@dataclass
class CloudFrontWebDistributionLogEntry(LogEntry):
    date: datetime.date
    time: datetime.time
    edge_location: str
    sent_bytes: int
    client_ip: str
    http_method: str
    host: str
    uri_stem: str
    status_code: int
    referrer: str
    user_agent: str
    uri_query: typing.Optional[dict]
    cookie: typing.Optional[cookies.SimpleCookie]
    edge_result_type: str
    edge_request_id: str
    host_header: str
    protocol: str
    received_bytes: typing.Optional[int]
    time_taken: float
    forwarded_for: typing.Optional[str]
    ssl_protocol: typing.Optional[str]
    ssl_cipher: typing.Optional[str]
    edge_response_result_type: str
    protocol_version: str
    fle_encrypted_fields: str = ""

    @property
    def timestamp(self):
        return datetime.datetime.fromisoformat(
            f"{self.date}T{self.time}",
        ).replace(tzinfo=datetime.timezone.utc)


@dataclass
class CloudFrontRTMPDistributionLogEntry(LogEntry):
    date: str
    time: str
    edge_location: str
    client_ip: str
    event: str
    sent_bytes: int
    status_code: str
    client_id: str
    uri_stem: str
    uri_query: dict
    referrer: str
    page_url: str
    user_agent: str


@dataclass
class LogFormat:
    name: str
    model: typing.Type[LogEntry]
    delimiter: str


@dataclass
class LogType:
    ClassicLoadBalancer: LogFormat = LogFormat(
        name="ClassicLoadBalancer",
        model=ClassicLoadBalancerLogEntry,
        delimiter=" ",
    )

    LoadBalancer: LogFormat = LogFormat(
        name="LoadBalancer",
        model=LoadBalancerLogEntry,
        delimiter=" ",
    )

    CloudFront: LogFormat = LogFormat(
        name="CloudFront",
        model=CloudFrontWebDistributionLogEntry,
        delimiter="\t",
    )

    CloudFrontRTMP: LogFormat = LogFormat(
        name="CloudFrontRTMP",
        model=CloudFrontRTMPDistributionLogEntry,
        delimiter="\t",
    )
