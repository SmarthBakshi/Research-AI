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