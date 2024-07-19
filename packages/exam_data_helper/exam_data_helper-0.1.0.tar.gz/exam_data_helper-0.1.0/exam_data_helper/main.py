import boto3
from botocore.exceptions import ClientError
from mypy_boto3_dynamodb import DynamoDBClient
from mypy_boto3_s3.client import S3Client
from typing import Any, Dict, Literal, Tuple
import numpy as np
import json
import logging
import os
import tempfile
import shutil
from typing import TypedDict
from transform_data import load_wav_file
from s3_helper import S3Helper
from dynamo_helper import DynamoHelper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("exam_data.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# source types for type hinting
SourceType = Literal["exam_id", "s3", "local"]


class ExamData:
    """No matter what the source type is, the EXAM_DETAILS is always loaded from the S3 bucket.
    - EXAM_DETAILS.json is the source of truth for the exam data
    - if it is an exam_id, the exam_id is used to query the dynamodb table to get the patient_id
    - if it is an s3 path, the path is used to get the EXAM_DETAILS
    - if it is a local directory, the EXAM_DETAILS is loaded from the local directory
    """

    def __init__(
        self, source_type: SourceType, source_value: str, region_name: str = "us-east-2"
    ):
        self.temp_dir = tempfile.mkdtemp()
        logger.info(f"Temporary directory created at {self.temp_dir}")
        self.source_type = source_type
        self.source_value = source_value
        self.region_name = region_name
        self.data: Dict[str, Any] = {}
        self.dynamo_client: DynamoDBClient = boto3.client(
            "dynamodb", region_name=self.region_name
        )
        self.s3_client: S3Client = boto3.client("s3", region_name=self.region_name)
        self.dynamo_helper = None
        self.s3_helper = S3Helper(
            bucket_name="digibeat-staging-uploads",
            s3_client=self.s3_client,
            folder_path="",
            tmp_path=self.temp_dir,
        )
        self.exam_details_json = None

        if source_type == "exam_id":
            self._initialize_from_exam_id(source_value)
        elif source_type == "s3":
            self._initialize_from_s3(source_value)
        elif source_type == "local":
            self._initialize_from_local(source_value)
        else:
            raise ValueError("Invalid source type provided")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    def cleanup(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            logger.info(f"Temporary directory {self.temp_dir} has been removed")

    def _initialize_from_exam_id(self, exam_id: str):
        try:
            logger.info(f"Data initialized using exam ID: {exam_id}")
            self.dynamo_helper = DynamoHelper(self.dynamo_client)
            response = self.dynamo_helper.get_exam_details(exam_id)
            self.data.update(response)
            # self.data[response] = response
            s3_path = f"PATIENT#{self.data['PATIENT_ID']}/EXAM#{exam_id}"
            self._initialize_from_s3(s3_path)
        except ClientError as e:
            logger.error(f"An error occurred: {e}")
            raise

    def _initialize_from_s3(self, s3_path):
        exam_details_path = self.s3_helper.get_exam_details()

        if exam_details_path != None:
            # self.exam_details_json = exam_details_path
            with open(exam_details_path, "r") as f:
                self.exam_details_json = json.load(f)

        logger.info(f"Data loaded from S3: {s3_path}")

    def _initialize_from_local(self, local_dir: str):
        try:
            for root, _, files in os.walk(local_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    if file.endswith(".json"):
                        with open(file_path, "r") as f:
                            self.data.update(json.load(f))
                    else:
                        shutil.copy(file_path, self.temp_dir)
            logger.info(f"Data loaded from local directory: {local_dir}")
        except Exception as e:
            logger.error(f"Error loading data from local directory: {e}")
            raise

    def download_exam_ambient_noise(self) -> str:
        try:
            if (self.source_type == "exam_id") or (self.source_type == "s3"):
                result = self.s3_helper.download_exam_ambient_noise()
                if result != None:
                    return result
                else:
                    raise FileNotFoundError("Ambient noise file not found")
            elif self.source_type == "local":
                logger.info("Ambient noise download not supported for local data")
            raise ValueError("Invalid source type provided")
        except Exception as e:
            logger.error(f"An error occurred while downloading ambient noise: {e}")
            raise

    def get_exam_voltage_data(self) -> Tuple[int, np.ndarray]:
        """returns the voltage data from the exam in the form of a numpy array and the sampling rate

        Raises:
            FileNotFoundError: file not found
            ValueError: invalid source type

        Returns:
            Tuple[int, np.ndarray]: numpy array and sampling rate
        """
        try:
            if (self.source_type == "exam_id") or (self.source_type == "s3"):
                result_path = self.s3_helper.download_ble_stream_voltage()
                if result_path != None:
                    return load_wav_file(result_path)
                else:
                    raise FileNotFoundError("Voltage data file not found")
            elif self.source_type == "local":
                logger.info("Voltage data download not supported for local data")
            raise ValueError("Invalid source type provided")
        except Exception as e:
            logger.error(f"An error occurred while downloading voltage data: {e}")
            raise

    def get_exam_audio_data(self) -> Tuple[int, np.ndarray]:
        """returns the audio data from the exam in the form of a buffer and the sampling rate

        Raises:
            FileNotFoundError: file not found
            ValueError: invalid source type

        Returns:
            Tuple[Buffer, int]: buffer and sampling rate
        """
        try:
            if (self.source_type == "exam_id") or (self.source_type == "s3"):
                result_path = self.s3_helper.download_ble_stream_audio()
                if result_path != None:
                    return load_wav_file(result_path)
                else:
                    raise FileNotFoundError("Audio data file not found")
            elif self.source_type == "local":
                logger.info("Audio data download not supported for local data")
            raise ValueError("Invalid source type provided")
        except Exception as e:
            logger.error(f"An error occurred while downloading audio data: {e}")
            raise

    def get_exam_details(self) -> Dict[str, Any] | None:
        """returns the exam details

        Returns:
            Dict[str, Any] | None: exam details
        """
        return self.exam_details_json
