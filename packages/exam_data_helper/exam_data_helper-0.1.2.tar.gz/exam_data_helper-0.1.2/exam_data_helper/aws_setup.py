# dynamodb_client.py
import boto3
from mypy_boto3_dynamodb import DynamoDBClient
from mypy_boto3_s3.client import S3Client

class dynamodb_client:
    _client = None

    @classmethod
    def get_client(cls, region_name: str) -> DynamoDBClient:
        if cls._client is None:
            cls._client = boto3.client("dynamodb", region_name=region_name)
        return cls._client
    
class s3_client:
    _client = None

    @classmethod
    def get_client(cls, region_name: str) -> S3Client:
        if cls._client is None:
            cls._client = boto3.client("s3", region_name=region_name)
        return cls._client
