import os
from deltalake import DeltaTable, write_deltalake
import pyarrow as pa
from dotenv import load_dotenv


def manual():
    load_dotenv()
    # write some data into a delta table
    df = pa.table({"id": [1, 2], "value": ["foo", "bar"]})
    print(df)

    storage_options = {
        "AWS_ACCESS_KEY_ID": os.getenv("STORAGE_ACCESS_KEY_ID", ""),
        "AWS_SECRET_ACCESS_KEY": os.getenv("STORAGE_SECRET_ACCESS_KEY", ""),
        "AWS_ENDPOINT_URL": os.getenv("STORAGE_ENDPOINT_URL", ""),
        "AWS_REGION": "local",
        "AWS_S3_ALLOW_UNSAFE_RENAME": "true",
        "AWS_ALLOW_HTTP": "true"
    }
    write_deltalake("s3a://test/pa/", df, storage_options=storage_options, mode="overwrite")
    print("\nData written\n")
    # read the data back
    table = DeltaTable("s3a://test/pa/", storage_options=storage_options)
    print(table.to_pyarrow_table())


if __name__ == "__main__":
    manual()
