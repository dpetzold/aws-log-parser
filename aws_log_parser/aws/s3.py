import re

from dataclasses import dataclass
from io import BytesIO

from .client import (
    AwsClient,
    AwsService,
)
from ..io import FileIterator


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

    def read_key(self, bucket, key):
        if self.aws_client.verbose:
            print(f"Reading s3://{bucket}/{key}")
        contents = self.client.get_object(Bucket=bucket, Key=key)
        yield from FileIterator(
            fileobj=BytesIO(contents["Body"].iter_lines()),
            gzipped=key.endswith(".gz"),
        )

    def read_keys(self, bucket, prefix, endswith=None, regex_filter=None):
        reo = re.compile(regex_filter) if regex_filter else None
        for file in self.list_files(bucket, prefix, "LastModified"):
            if endswith and not file["Key"].endswith(endswith):
                continue

            if reo and not reo.match(file):
                continue

            yield from self.read_key(bucket, file["Key"])
