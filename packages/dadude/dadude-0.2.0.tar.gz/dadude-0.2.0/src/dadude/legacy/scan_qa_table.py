import os
import boto3
from fire import Fire
from dotenv import load_dotenv
from decimal import Decimal
import json


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return str(o)
        return json.JSONEncoder.default(self, o)


def main():
    load_dotenv()
    table_name = os.environ.get("DB_TABLE_NAME", "")
    target_dir = os.environ.get("TG_DIR", "")
    target_path = table_name + ".json"
    db = boto3.resource(
        "dynamodb",
        aws_access_key_id=os.environ.get("DB_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("DB_SECRET_ACCESS_KEY"),
        region_name=os.environ.get("DB_REGION"),
        endpoint_url=os.environ.get("DB_ENDPOINT_URL"),
    )
    table = db.Table(table_name) # type: ignore
    response = table.scan()
    to_write = response.get("Items")
    with open(f"{target_dir}/{target_path}", "wt") as f:
        json.dump(to_write, f, indent=4, cls=DecimalEncoder, ensure_ascii=False)


if __name__ == "__main__":
    Fire(main)
