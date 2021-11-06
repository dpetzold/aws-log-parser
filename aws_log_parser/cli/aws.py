import boto3
import boto3.session

from dataclasses import dataclass

ec2_client = boto3.client("ec2")


@dataclass
class AwsClient:

    region: str
    profile: str

    def aws_session(self):
        return boto3.session.Session(region_name=self.region, profile_name=self.profile)

    def aws_client(self, service_name):
        return self.aws_session.client(service_name)

    def get_tag(self, tags, name):
        for tag in tags:
            if tag["Key"] == name:
                return tag["Value"]
