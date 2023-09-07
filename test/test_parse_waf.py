import datetime
import pytest
import typing

from .conftest import parse_entry

from aws_log_parser.models import (
    LogType,
    WafLogEntry,
    WafLogEntryRuleGroup,
    WafLogEntryNonTerminatingMatchingRules,
    WafLogEntryNonTerminatingMatchingRule,
    WafLogEntryExcludedRules,
    WafLogEntryRateGroup,
    WafLogEntryHttpRequest,
    WafLogEntryHttpRequestHeader,
)


@pytest.fixture
def base_waf_entry():
    return WafLogEntry(
        timestamp=datetime.datetime(2018, 8, 8, 0, 44, 30, 589000),
        formatVersion=1,
        webaclId="385cb038-3a6f-4f2f-ac64-09ab912af590",
        terminatingRuleId="Default_Action",
        terminatingRuleType="REGULAR",
        action="ALLOW",
        httpSourceName="CF",
        httpSourceId="i-123",
        ruleGroupList=[
            WafLogEntryRuleGroup(
                ruleGroupId="41f4eb08-4e1b-2985-92b5-e8abf434fad3",
                terminatingRule=None,
                nonTerminatingMatchingRules=[
                    WafLogEntryNonTerminatingMatchingRules(
                        action="COUNT", ruleId="4659b169-2083-4a91-bbd4-08851a9aaf74"
                    )
                ],
                excludedRules=[
                    WafLogEntryExcludedRules(
                        exclusionType="EXCLUDED_AS_COUNT",
                        ruleId="5432a230-0113-5b83-bbb2-89375c5bfa98",
                    )
                ],
            )
        ],
        rateBasedRuleList=[
            WafLogEntryRateGroup(
                rateBasedRuleId="7c968ef6-32ec-4fee-96cc-51198e412e7f",
                limitKey="IP",
                maxRateAllowed=100,
            ),
            WafLogEntryRateGroup(
                rateBasedRuleId="462b169-2083-4a93-bbd4-08851a9aaf30",
                limitKey="IP",
                maxRateAllowed=100,
            ),
        ],
        nonTerminatingMatchingRules=[
            WafLogEntryNonTerminatingMatchingRule(
                action="COUNT", ruleId="4659b181-2011-4a91-bbd4-08851a9aaf52"
            )
        ],
        httpRequest=WafLogEntryHttpRequest(
            clientIp="192.10.23.23",
            country="US",
            headers=[
                WafLogEntryHttpRequestHeader(name="Host", value="127.0.0.1:1989"),
                WafLogEntryHttpRequestHeader(name="User-Agent", value="curl/7.51.2"),
                WafLogEntryHttpRequestHeader(name="Accept", value="*/*"),
            ],
            uri="REDACTED",
            args="usernam=abc",
            httpVersion="HTTP/1.1",
            httpMethod="GET",
            requestId="cloud front Request " "id",
        ),
    )


def test_waf_entry(waf_entry_json, base_waf_entry):
    waf_entry = typing.cast(WafLogEntry, parse_entry([waf_entry_json], LogType.WAF))
    assert isinstance(waf_entry.timestamp, datetime.datetime) is True
    assert waf_entry == base_waf_entry
