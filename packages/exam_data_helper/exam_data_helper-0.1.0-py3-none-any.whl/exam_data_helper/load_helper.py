import os
import logging
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.types import TypeDeserializer

logger = logging.getLogger(__name__)
s3_client = boto3.client("s3")
dynamodb_client = boto3.client("dynamodb")


class DataInitializer:

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

    @staticmethod
    def from_s3_directory(bucket: str, directory: str) -> dict:
        """Initialize data from an S3 directory."""
        data = {}
        try:
            response = s3_client.list_objects_v2(Bucket=bucket, Prefix=directory)
            for obj in response.get("Contents", []):
                key = obj.get("Key")
                if key and not key.endswith("/"):
                    file_obj = s3_client.get_object(Bucket=bucket, Key=key)
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
