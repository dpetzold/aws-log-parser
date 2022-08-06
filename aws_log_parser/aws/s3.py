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

        items = self.paginate(
            "s3",
            "list_objects_v2",
            "Contents",
            Bucket=bucket,
            Prefix=prefix,
        )

        return sorted(items, key=lambda x: x[sort_key], reverse=reverse)

    def read_key(self, bucket, key):
        if self.aws_client.verbose:
            print(f"Reading s3://{bucket}/{key}")
        contents = self.client.get_object(Bucket=bucket, Key=key)
        if key.endswith(".gz"):
            with gzip.open(contents["Body"], "rt") as f:
                yield from f.readlines()
        else:
            yield from [line.decode("utf-8") for line in contents["Body"].iter_lines()]

    def read_keys(self, bucket, prefix, endswith=None):

        for file in self.list_files(bucket, prefix, "LastModified"):
            if endswith and not file["Key"].endswith(endswith):
                continue

            yield self.read_key(bucket, file["Key"])
