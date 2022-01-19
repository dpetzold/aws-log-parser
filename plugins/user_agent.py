import logging

from dataclasses import dataclass, field

from aws_log_parser.plugin import AwsLogParserPlugin

from user_agents import parse
from user_agents.parsers import UserAgent


logger = logging.getLogger(__name__)


@dataclass
class UserAgentPlugin(AwsLogParserPlugin):
    """
    Resolve the hostname from the client ip address.
    """

    consumed_attr: str = "user_agent"
    produced_attr: str = field(default="user_agent_obj", metadata={"type": UserAgent})

    def query(self, user_agent):
        return parse(user_agent)
