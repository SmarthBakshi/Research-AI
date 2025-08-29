import os
from minio import Minio

# Load credentials from environment
access_key = os.environ.get("AWS_ACCESS_KEY_ID", "minio")
secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY", "minio123")
endpoint = os.environ.get("MINIO_ENDPOINT", "http://minio:9000")

# Remove 'http://' or 'https://' from endpoint if needed by Minio client
endpoint = endpoint.replace("http://", "").replace("https://", "")

client = Minio(
    endpoint,
    access_key=access_key,
    secret_key=secret_key,
    secure=False
)

def list_files(bucket_name, prefix=""):
    objects = client.list_objects(bucket_name, prefix=prefix, recursive=True)
    return [obj.object_name for obj in objects]

def download_file(bucket_name, object_name, local_path="tmp/"):
    local_file = f"{local_path}/{object_name.split('/')[-1]}"
    client.fget_object(bucket_name, object_name, local_file)
    return local_file

def ensure_bucket_exists(bucket_name: str, s3_client):
    """Create the MinIO bucket if it doesn't exist."""
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"✅ Bucket '{bucket_name}' already exists.")
    except s3_client.exceptions.ClientError as e:
        error_code = int(e.response['Error']['Code'])
        if error_code == 404:
            print(f"📦 Bucket '{bucket_name}' not found. Creating...")
            s3_client.create_bucket(Bucket=bucket_name)
            print(f"✅ Bucket '{bucket_name}' created.")
        else:
            raise e
