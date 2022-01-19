import logging

from dataclasses import dataclass

from aws_log_parser.plugin import AwsLogParserPlugin

from user_agents import parse, UserAgent


logger = logging.getLogger(__name__)


@dataclass
class UserAgentPlugin(AwsLogParserPlugin):
    """
    Resolve the hostname from the client ip address.
    """

    consumed_attr: str = "user_agent"
    produced_attr: UserAgent = "user_agent_model"

    def query(self, user_agent):
        return parse(user_agent)
