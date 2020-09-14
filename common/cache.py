import boto3
import json
import os


class LocalCache:
    def __init__(self, filename: str) -> None:
        self.filename = filename

    def log_last_processed_id(self, last_processed_id: int, last_processed_time_stamp: str):
        msg = {
            "last_processed_id": last_processed_id,
            "last_processed_time_stamp": last_processed_time_stamp,
        }
        with open(self.filename, "w") as f:
            f.write(json.dumps(msg))

    def log_last_processed_timestamp(self, last_processed_time_stamp: str):
        msg = {
            "last_processed_time_stamp": last_processed_time_stamp,
        }
        with open(self.filename, "w") as f:
            f.write(json.dumps(msg))

    def get_since_id_from_file(self):
        with open(self.filename, "r") as f:
            d = json.load(f)
        return d.get("last_processed_id")

    def get_last_processed_time_stamp_from_file(self):
        with open(self.filename, "r") as f:
            d = json.load(f)
        return d.get("last_processed_time_stamp")


class S3Cache:
    def __init__(self, filename: str, bucket: str):
        self.filename = filename
        self.bucket = bucket
        self.file = None
        self.client = boto3.client(
            "s3",
            # Hard coded strings as credentials, not recommended.
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS"),
        )
        self.local_cache = LocalCache(filename)

    def log_last_processed_id(self, last_processed_id: int, last_processed_time_stamp: str):
        self.local_cache.log_last_processed_id(last_processed_id, last_processed_time_stamp)

        response = self.client.upload_file(self.filename, self.bucket, self.filename)
        return response

    def log_last_processed_timestamp(self, last_processed_time_stamp: str):
        self.local_cache.log_last_processed_timestamp(last_processed_time_stamp)

        response = self.client.upload_file(self.filename, self.bucket, self.filename)
        return response

    def get_since_id_from_file(self):
        self.client.download_file(
            self.bucket, self.filename, self.filename,
        )
        return self.local_cache.get_since_id_from_file()

    def get_last_processed_time_stamp_from_file(self):
        self.client.download_file(
            self.bucket, self.filename, self.filename,
        )
        return self.local_cache.get_last_processed_time_stamp_from_file()
