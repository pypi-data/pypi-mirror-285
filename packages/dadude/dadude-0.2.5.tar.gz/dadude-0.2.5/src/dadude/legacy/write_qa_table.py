import os
import gzip
from decimal import Decimal
import json
import boto3
from tqdm import tqdm
from fire import Fire
from loguru import logger
from dotenv import load_dotenv


SAMPLE_ROWS = 1000
DECIMAL_PRECISION = 2


def float2decimal(s):
    return Decimal(str(round(float(s), DECIMAL_PRECISION)))


def str2gz(text):
    """
    str to Dynamodb binary
    :param text: text to compress
    :return:
    """
    data = text.encode("utf-8")
    gziped = gzip.compress(data)
    return gziped


def gz2str(data):
    """
    Dynamodb binary to str
    :param data: byte[]
    :return: string
    """
    flat = gzip.decompress(data)
    return flat.decode("utf-8")


def main(
    input_file,
    table_name,
    uid,
    limit=SAMPLE_ROWS,
    lines=True,
):
    load_dotenv()
    db = boto3.resource(
        "dynamodb",
        aws_access_key_id=os.environ.get("QA_DB_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("DB_SECRET_ACCESS_KEY"),
        region_name=os.environ.get("DB_REGION"),
        endpoint_url=os.environ.get("QA_DB_ENDPOINT_URL"),
    )
    logger.info(f"Connected to {db.meta.client.meta.endpoint_url}")     # type: ignore
    table = db.Table(table_name)  # type: ignore
    logger.info(f"Table: {table.name}")
    # start writing to table
    with open(input_file) as f:
        written = 0
        rows = []
        if lines:
            for line in f:
                rows.append(json.loads(line, parse_float=float2decimal))
        else:
            rows = json.load(f, parse_float=float2decimal)
        for entry in tqdm(rows):
            if written > limit:
                break
            response = table.put_item(Item=entry)
            if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                written += 1
            else:
                logger.error(f"Failed to write {entry[uid]}")


if __name__ == "__main__":
    Fire(main)
