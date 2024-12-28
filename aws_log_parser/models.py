import datetime
import typing
from enum import (
    Enum,
    auto,
)

from dataclasses_json import DataClassJsonMixin, config, dataclass_json
from dataclasses import dataclass, field
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
    AuthInvalidAWSALBAuthNonce = auto()
    AuthInvalidCookie = auto()
    AuthInvalidGrantError = auto()
    AuthInvalidIdToken = auto()
    AuthInvalidStateParam = auto()
    AuthInvalidTokenResponse = auto()
    AuthInvalidUserinfoResponse = auto()
    AuthMissingAWSALBAuthNonce = auto()
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
class LogEntry(DataClassJsonMixin):
    pass


@dataclass(frozen=True)
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


@dataclass(frozen=True)
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
    target_group_arn: typing.Optional[str]
    trace_id: str
    domain_name: typing.Optional[str]
    chosen_cert_arn: typing.Optional[str]
    matched_rule_priority: int
    request_creation_time: datetime.datetime
    actions_executed: typing.List[str]
    redirect_url: typing.Optional[str]
    error_reason: typing.Optional[LoadBalancerErrorReason]


@dataclass(frozen=True)
class CloudFrontLogEntry(LogEntry):
    date: datetime.date
    time: datetime.time

    @property
    def timestamp(self):
        return datetime.datetime.fromisoformat(
            f"{self.date}T{self.time}",
        ).replace(tzinfo=datetime.timezone.utc)


@dataclass(frozen=True)
class CloudFrontWebDistributionLogEntry(CloudFrontLogEntry):
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


@dataclass(frozen=True)
class CloudFrontRTMPDistributionLogEntry(CloudFrontLogEntry):
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


# Begin WAF


@dataclass_json
@dataclass(frozen=True)
class WafLogEntryNonTerminatingMatchingRules:
    action: str
    ruleId: str


@dataclass_json
@dataclass(frozen=True)
class WafLogEntryExcludedRules:
    exclusionType: str
    ruleId: str


@dataclass_json
@dataclass(frozen=True)
class WafLogEntryRuleGroup:
    ruleGroupId: str
    terminatingRule: typing.Optional[str]
    nonTerminatingMatchingRules: typing.List[WafLogEntryNonTerminatingMatchingRules]
    excludedRules: typing.List[WafLogEntryExcludedRules]


@dataclass_json
@dataclass(frozen=True)
class WafLogEntryRateGroup:
    rateBasedRuleId: str
    limitKey: str
    maxRateAllowed: int


@dataclass_json
@dataclass(frozen=True)
class WafLogEntryNonTerminatingMatchingRule:
    action: str
    ruleId: str


@dataclass_json
@dataclass(frozen=True)
class WafLogEntryHttpRequestHeader:
    name: str
    value: str


@dataclass_json
@dataclass(frozen=True)
class WafLogEntryHttpRequest:
    clientIp: str
    country: str
    headers: typing.List[WafLogEntryHttpRequestHeader]
    uri: str
    args: str
    httpVersion: str
    httpMethod: str
    requestId: str


@dataclass_json
@dataclass(frozen=True)
class WafLogEntry(LogEntry):
    timestamp: datetime.datetime = field(
        metadata=config(
            encoder=lambda t: datetime.datetime.timestamp(t) * 1000,
            decoder=lambda t: datetime.datetime.fromtimestamp(
                t / 1000,
                datetime.timezone.utc,
            ),
        )
    )
    formatVersion: int
    webaclId: str
    terminatingRuleId: str
    terminatingRuleType: str
    action: str
    httpSourceName: str
    httpSourceId: str
    httpRequest: WafLogEntryHttpRequest
    ruleGroupList: typing.List[WafLogEntryRuleGroup] = field(default_factory=list)
    rateBasedRuleList: typing.List[WafLogEntryRateGroup] = field(default_factory=list)
    nonTerminatingMatchingRules: typing.List[WafLogEntryNonTerminatingMatchingRule] = (
        field(default_factory=list)
    )

    @property
    def client_ip(self):
        return self.httpRequest.clientIp


class LogFormatType(str, Enum):
    CSV = "CSV"
    JSON = "JSON"


@dataclass
class LogFormat:
    name: str
    model: typing.Type[LogEntry]
    type: LogFormatType
    delimiter: typing.Optional[str] = None


def LogFormatCsv(**kwargs):
    return LogFormat(type=LogFormatType.CSV, **kwargs)


def LogFormatJson(**kwargs):
    return LogFormat(type=LogFormatType.JSON, **kwargs)


def LogFormatCsvSpaced(**kwargs):
    return LogFormatCsv(delimiter=" ", **kwargs)


def LogFormatCsvTabbed(**kwargs):
    return LogFormatCsv(delimiter="\t", **kwargs)


@dataclass
class LogType:
    ClassicLoadBalancer: typing.ClassVar[LogFormat] = LogFormatCsvSpaced(
        name="ClassicLoadBalancer",
        model=ClassicLoadBalancerLogEntry,
    )

    LoadBalancer: typing.ClassVar[LogFormat] = LogFormatCsvSpaced(
        name="LoadBalancer",
        model=LoadBalancerLogEntry,
    )

    CloudFront: typing.ClassVar[LogFormat] = LogFormatCsvTabbed(
        name="CloudFront",
        model=CloudFrontWebDistributionLogEntry,
    )

    CloudFrontRTMP: typing.ClassVar[LogFormat] = LogFormatCsvTabbed(
        name="CloudFrontRTMP",
        model=CloudFrontRTMPDistributionLogEntry,
    )

    WAF: typing.ClassVar[LogFormat] = LogFormatJson(
        name="WAF",
        model=WafLogEntry,
    )
