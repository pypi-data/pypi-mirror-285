import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from mypy_boto3_dynamodb import DynamoDBClient
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from typing import Any, Dict
import logging


class DynamoHelper:
    """This class helps to interact with the DynamoDB table that contains the exam data."""

    def __init__(self, dynamo_client):
        self.client: DynamoDBClient = dynamo_client
        # self.table_name = table_name
        self.deserializer = TypeDeserializer()
        self.serializer = TypeSerializer()
        logging.basicConfig(level=logging.INFO)

    def get_exam_details(self, exam_id: str) -> Dict[str, Any]:
        """This function gets the exam details from the DynamoDB table.

        Args:
            exam_id: The exam_id for which the details are to be fetched.

        Returns:
            A dictionary with the exam details.
        """
        try:
            data = {}
            response = self.client.query(
                TableName="main-staging",
                ExpressionAttributeValues={
                    ":PK": {"S": f"EXAM#{exam_id}"},
                    ":SK": {"S": "PROFILE"},
                },
                KeyConditionExpression="PK = :PK and SK = :SK",
            )
            deserializer = TypeDeserializer()
            for item in response["Items"]:
                for key, value in item.items():
                    data[key] = deserializer.deserialize(value)
            return data
        except NoCredentialsError:
            logging.error("Credentials not available")
            return {}
        except ClientError as e:
            logging.error(f"An error occurred: {e}")
            return {}
