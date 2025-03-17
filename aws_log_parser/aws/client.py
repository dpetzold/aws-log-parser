import boto3
import boto3.session
import typing

from dataclasses import dataclass


@dataclass
class AwsClient:
    region: typing.Optional[str] = None
    profile: typing.Optional[str] = None
    verbose: bool = False

    @property
    def aws_session(self):
        return boto3.session.Session(region_name=self.region, profile_name=self.profile)

    def aws_client(self, service_name):
        return self.aws_session.client(service_name)

    def get_tag(self, tags, name):
        for tag in tags:
            if tag["Key"] == name:
                return tag["Value"]
