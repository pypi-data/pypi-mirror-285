# LOAD httpfs;
# SET s3_region='us-east-1';
# SET s3_url_style='path';
# SET s3_endpoint='192.168.18.206:9000';
# SET s3_access_key_id='iamdev';
# SET s3_secret_access_key='xzd19950506';
# SET s3_use_ssl=false;

from dadude.reader.duck_client import Quack


if __name__ == "__main__":
    quack = Quack()
    quack.client.execute("""
        LOAD httpfs;
        INSTALL delta;
        LOAD delta;
    """)
    quack.client.execute("""CREATE SECRET my_secret (
    TYPE S3,
    KEY_ID 'iamdev',
    SECRET 'xzd19950506',
    REGION '',
    USE_SSL false,
    URL_STYLE 'path',
    ENDPOINT '192.168.18.206:9000'
);""")
    delta_table_path = "s3a://test/property"
    print(quack._sql(
        "select * from read_parquet('s3a://test/property/0-733054a2-a87a-4a26-91f7-aa86a2f501cd-0.parquet')"
    ))
    dump = quack._sql(f"select * from delta_scan('{delta_table_path}')").to_json()
    print(dump)
