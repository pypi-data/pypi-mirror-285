import pytest
from dadude.primitives import ObjectStorageClient


@pytest.fixture
def self_hosted_minio_client():
    minio_config = {
        "access_key": "iamdev",
        "secret_key": "xzd19950506",
        "endpoint_url": "https://s3.completenonsense.net",
    }
    my_client = ObjectStorageClient.from_config(minio_config)
    return my_client


@pytest.fixture
def patsnap_ceph_client():
    patsnap_ceph_config = {
        "access_key": "k2W8hPYxUP5NTbFB",
        "secret_key": "icrIfxbLNv8gtURdRkFJH3lbIWMSixDT",
        "endpoint_url": "http://local-minio-s3-api.patsnap.io",
    }
    client = ObjectStorageClient.from_config(patsnap_ceph_config)
    return client


@pytest.fixture
def materials_bucket_prefix():
    return "local-rd-common/matter-most"


def test_ceph_client_list_bucket(patsnap_ceph_client):
    buckets = patsnap_ceph_client.list_buckets()["Buckets"]
    assert len(buckets) == 4
    bucket_names = [b["Name"] for b in buckets]
    # if this fails, new buckets have been added to the minio instance
    assert bucket_names == [
        "llm-model",
        "local-llm",
        "local-rd-common",
        "local-rd-datasets",
    ]


def test_ceph_client_list_resources(patsnap_ceph_client, materials_bucket_prefix):
    bucket, prefix = materials_bucket_prefix.split("/", 1)
    all_objects = patsnap_ceph_client.list_objects_v2(
        Bucket=bucket,
        Delimiter="/",
        Prefix=prefix,
    )
    print(all_objects)