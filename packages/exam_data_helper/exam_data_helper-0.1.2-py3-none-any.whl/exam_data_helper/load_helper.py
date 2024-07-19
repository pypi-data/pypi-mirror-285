import os
import logging
from botocore.exceptions import ClientError
from exam_data_helper.aws_setup import s3_client

logger = logging.getLogger(__name__)


class DataInitializer:
    def __init__(
        self, region_name: str = "us-east-2"
    ):
        self.region_name = region_name

    @staticmethod
    def from_local_directory(directory: str) -> dict:
        """Initialize data from a local directory."""
        data = {}
        try:
            for filename in os.listdir(directory):
                filepath = os.path.join(directory, filename)
                if os.path.isfile(filepath):
                    with open(filepath, "r") as file:
                        data[filename] = file.read()
            logger.info(f"Data initialized from local directory: {directory}")
        except Exception as e:
            logger.error(f"An error occurred while reading from local directory: {e}")
            raise
        return data
    
    def from_s3_directory(self, bucket: str, directory: str) -> dict:
        """Initialize data from an S3 directory."""
        data = {}
        try:
            client = s3_client.get_client(self.region_name)
            response = client.list_objects_v2(Bucket=bucket, Prefix=directory)
            for obj in response.get("Contents", []):
                key = obj.get("Key")
                if key and not key.endswith("/"):
                    file_obj = client.get_object(Bucket=bucket, Key=key)
                    data[key] = file_obj["Body"].read().decode("utf-8")
            logger.info(
                f"Data initialized from S3 bucket: {bucket}, directory: {directory}"
            )
        except ClientError as e:
            logger.error(f"An error occurred while reading from S3: {e}")
            raise
        return data

    @staticmethod
    def from_stream(multipart_upload_stream_obj) -> dict:
        """Initialize data from a stream (e.g., multipart upload)."""
        data = {}
        try:
            data["stream_data"] = multipart_upload_stream_obj.read().decode("utf-8")
            logger.info("Data initialized from stream.")
        except Exception as e:
            logger.error(f"An error occurred while reading from stream: {e}")
            raise
        return data
