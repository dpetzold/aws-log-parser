from dataclasses import dataclass

from .aws import AwsClient


@dataclass
class S3Client:

    bucket: str
    prefix: str

    aws_client: AwsClient

    @property
    def client(self):
        return self.aws_client.aws_client("s3")

    def list_files(self, sort_key, reverse=True):

        paginator = self.client.get_paginator("list_objects_v2",).paginate(
            Bucket=self.bucket,
            Prefix=self.prefix,
        )

        items = [item for page in paginator for item in page["Contents"]]

        return sorted(items, key=lambda x: x[sort_key], reverse=reverse)

    def read_key(self, key):
        contents = self.client.get_object(Bucket=self.bucket, Key=key)
        yield from [line.decode("utf-8") for line in contents["Body"].iter_lines()]

    def read_keys(self, endswith=None):

        files = self.list_files("LastModified")

        for file in files:
            if endswith and not file["Key"].endswith(endswith):
                continue

            print(f"{self.bucket}/{file['Key']}")
            yield from self.read_key(file["Key"])
