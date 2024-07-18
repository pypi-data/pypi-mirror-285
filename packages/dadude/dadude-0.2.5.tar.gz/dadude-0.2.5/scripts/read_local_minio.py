import os
from dotenv import load_dotenv
from loguru import logger
import boto3
from dadude.primitives import ObjectStorageClient


def manual():
    load_dotenv()
    access_key = os.getenv("STORAGE_ACCESS_KEY_ID")
    secret_key = os.getenv("STORAGE_SECRET_ACCESS_KEY")
    endpoint = os.getenv("STORAGE_ENDPOINT_URL", "")
    logger.debug(f"{access_key=}, {secret_key=}, {endpoint=}")
    session = boto3.client(
        "s3",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        endpoint_url=endpoint,
    )
    bucket_response = session.list_buckets()
    # logger.debug(f"{bucket_response=}")
    print([b["Name"] for b in bucket_response.get("Buckets", [])])


def enclosure():
    conn_client = ObjectStorageClient.from_env()
    print(conn_client.list_buckets())


if __name__ == "__main__":
    # manual()
    enclosure()