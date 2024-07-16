import subprocess
from dadude.primitives import ObjectStorageClient


if __name__ == "__main__":
    conn_client = ObjectStorageClient.from_env()
    bucket_name = "matter-most"
    # collection of directories
    directory_names = [
        "inbox",
        "bronze",
        "silver",
        "gold",
        "evaluation",
        "staging",
    ]
    for dir_name in directory_names:
        conn_client.put_object(Bucket=bucket_name, Key=(dir_name + "/"))
    # check if the folders are created
    subprocess.run(["bash", "/home/kevinxu/hack/min3", "ls", "s3://matter-most/"])