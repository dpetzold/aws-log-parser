import boto3
import boto3.session

import importlib

from dataclasses import dataclass


@dataclass
class AwsClient:

    region: str
    profile: str

    @property
    def aws_session(self):
        return boto3.session.Session(region_name=self.region, profile_name=self.profile)

    def aws_client(self, service_name):
        return self.aws_session.client(service_name)

    def get_service(self, service_name):
        try:
            module = importlib.import_module(f".{service_name}")
            service = getattr(module, f"{service_name.title()}Service")
        except (ImportError, AttributeError):
            raise ValueError(f"Unknown service {service_name}")
        return service

    def service_factory(self, service_name):
        return self.get_service(service_name)(aws_client=self)


@dataclass
class AwsService:

    aws_client: AwsClient

    def get_tag(self, tags, name):
        for tag in tags:
            if tag["Key"] == name:
                return tag["Value"]
