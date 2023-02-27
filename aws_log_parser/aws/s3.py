import gzip

from dataclasses import dataclass

from .client import (
    AwsClient,
    AwsService,
)


@dataclass
class S3Service(AwsService):
    aws_client: AwsClient

    @property
    def client(self):
        return self.aws_client.aws_client("s3")

    def list_files(self, bucket, prefix, sort_key, reverse=True):
        paginator = self.client.get_paginator("list_objects_v2").paginate(
            Bucket=bucket,
            Prefix=prefix,
        )

        items = [item for page in paginator for item in page["Contents"]]

        return sorted(items, key=lambda x: x[sort_key], reverse=reverse)

    def read_key(self, bucket, key, endswith=None):
        if self.aws_client.verbose:
            print(f"Reading s3://{bucket}/{key}")
        contents = self.client.get_object(Bucket=bucket, Key=key)
        if endswith == ".gz":
            with gzip.GzipFile(fileobj=contents["Body"]) as _gz:
                yield from [line for line in _gz.read().decode("utf-8").splitlines()]
        else:
            yield from [line.decode("utf-8") for line in contents["Body"].iter_lines()]

    def read_keys(self, bucket, prefix, endswith=None):
        for file in self.list_files(bucket, prefix, "LastModified"):
            if endswith and not file["Key"].endswith(endswith):
                continue

            yield from self.read_key(bucket, file["Key"], endswith)
