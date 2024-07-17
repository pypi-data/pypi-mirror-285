import os
from dotenv import load_dotenv
from dataclasses import dataclass
import boto3


load_dotenv()


@dataclass
class ObjectStorageClient:
    access_key: str
    secret_key: str
    endpoint_url: str | None = None
    use_proxy: bool = False

    def __post_init__(self):
        self.client = boto3.client(
            "s3",
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            endpoint_url=self.endpoint_url,
        )

    @classmethod
    def from_config(cls, dict_config: dict):
        if "use_proxy" not in dict_config:
            dict_config["use_proxy"] = False
        return cls(
            dict_config["access_key"],
            dict_config["secret_key"],
            dict_config["endpoint_url"],
            dict_config["use_proxy"],
        ).client

    @classmethod
    def from_env(cls):
        return cls(
            os.getenv("STORAGE_ACCESS_KEY_ID", ""),
            os.getenv("STORAGE_SECRET_ACCESS_KEY", ""),
            os.getenv("STORAGE_ENDPOINT_URL"),
        ).client

    # Bucket level operations
    def list_buckets(self):
        return self.client.list_buckets()

    def create_bucket(self, bucket: str):
        return self.client.create_bucket(Bucket=bucket)

    def delete_bucket(self, bucket: str):
        return self.client.delete_bucket(Bucket=bucket)

    # Object level operations
    def list_objects_v2(self, **kwargs):
        return self.client.list_objects_v2(**kwargs)

    def get_object(self, **kwargs):
        return self.client.get_object(**kwargs)

    def put_object(self, **kwargs):
        return self.client.put_object(**kwargs)


@dataclass
class S3RemoteObject:
    name: str
    last_modified_date: str
    last_modified_time: str
    size: int
    storage_class: str = "STANDARD"
    prefix: str = ""

    @classmethod
    def from_response(cls, s3_response: dict, prefix):
        return cls(
            s3_response["Key"],
            s3_response["LastModified"].strftime("%Y-%m-%d"),
            s3_response["LastModified"].strftime("%H:%M:%S"),
            s3_response["Size"],
            s3_response["StorageClass"],
            prefix,
        )

    @staticmethod
    def parse_size_unit(size):
        if size < 1024:
            return str(size) + "B"
        elif size < 1024**2:
            return str(size // 1024) + "KB"
        elif size < 1024**3:
            return str(size // 1024**2) + "MB"
        else:
            return str(size // 1024**3) + "GB"

    def __str__(self):
        return "\t".join(
            (
                self.last_modified_date,
                self.last_modified_time,
                self.parse_size_unit(self.size),
                self.name[len(self.prefix) :],
            )
        )


if __name__ == "__main__":
    minio_config = {
        "access_key": "iamdev",
        "secret_key": "xzd19950506",
        # "endpoint_url": "https://s3.completenonsense.net",
        "endpoint_url": "http://192.168.18.206:9000",
    }
    my_client = ObjectStorageClient.from_config(minio_config)
    all_objects = my_client.list_objects_v2(
        Bucket="matter-most",
        Delimiter="/",
        Prefix="bronze/",
    )["Contents"]
    print(all_objects)
