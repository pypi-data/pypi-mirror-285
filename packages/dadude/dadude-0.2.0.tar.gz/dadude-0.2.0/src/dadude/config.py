import os
from dotenv import load_dotenv


load_dotenv()

default_storage_config = {
    "AWS_ACCESS_KEY_ID": os.getenv("STORAGE_ACCESS_KEY_ID", ""),
    "AWS_SECRET_ACCESS_KEY": os.getenv("STORAGE_SECRET_ACCESS_KEY", ""),
    "AWS_ENDPOINT_URL": os.getenv("STORAGE_ENDPOINT_URL", ""),
    "AWS_REGION": "local",
    "AWS_S3_ALLOW_UNSAFE_RENAME": "true",
    "AWS_ALLOW_HTTP": "true",
}