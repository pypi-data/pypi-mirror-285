from fileinput import filename
from typing import Optional
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import json
import logging
import shutil
import os
from mypy_boto3_s3 import S3Client


class S3Helper:
    def __init__(self, folder_path, tmp_path, s3_client, bucket_name):
        self.client: S3Client = s3_client
        self.folder_path = folder_path
        self.bucket_name = bucket_name
        self.keys = self.list_object_keys()
        self.EXAM_DETAILS = None
        self.path = tmp_path
        logging.basicConfig(level=logging.INFO)

    def __enter__(self):
        return self

    # def __exit__(self, exc_type, exc_val, exc_tb):
    #     self.cleanup()

    # def cleanup(self):
    #     if os.path.exists(self.temp_dir):
    #         shutil.rmtree(self.temp_dir)
    #         logging.info(f"Deleted temp directory: {self.temp_dir}")

    def list_object_keys(self):
        """This function lists all the keys at the specified folder path in the S3 bucket.
        function runs when the class is initialized.

        Returns:
            a dictionary with a nested 'Contents' key that hass a list of dictionaries with 'Key' key.
        """
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name, Prefix=self.folder_path
            )
            keys = [
                obj.get("Key") for obj in response.get("Contents", []) if obj.get("Key")
            ]
            return keys
        except NoCredentialsError:
            logging.error("Credentials not available")
            return []
        except ClientError as e:
            logging.error(f"An error occurred: {e}")
            return []

    def download_file(self, keyword: str) -> str:
        try:
            for key in self.keys:
                if isinstance(key, str) and keyword in key:
                    filename = str(key).split("/")[-1]
                    file_type = filename.split(".")[-1]
                    saved_path = f"{self.path}/{keyword}.{file_type}"
                    self.client.download_file(
                        self.bucket_name, Key=str(key), Filename=saved_path
                    )

                    print(len(saved_path) == 0, "json check length")
                    logging.info(f"Downloaded '{key}' to '{saved_path}'")
                    return saved_path
            raise FileNotFoundError(f"File with keyword {keyword} not found")
        except NoCredentialsError:
            logging.error("Credentials not available")
            raise FileNotFoundError("Credentials not available")
        except ClientError as e:
            logging.error(f"An error occurred: {e}")
            raise FileNotFoundError(f"An error occurred: {e}")

    def download_all_files(self):
        """Download all files from the given list of S3 objects."""
        try:
            for key in self.keys:
                if key:
                    logging.info(f"Downloading file with key: {key}")
                    # filename = f"{self.path}/{key.split('/')[-1]}"
                    filename = f"test/{key.split('/')[-1]}"
                    self.client.download_file(
                        self.bucket_name, Key=str(key), Filename=filename
                    )
        except NoCredentialsError:
            logging.error("Credentials not available")
        except ClientError as e:
            logging.error(f"An error occurred: {e}")
            return False

    def download_exam_ambient_noise(self):
        """Download EXAM_AMBIENT.wav file from S3"""
        return self.download_file("EXAM_AMBIENT")

    def download_ble_stream_motion(self):
        """Download BLE_STREAM_MOTION.wav file from S3"""
        return self.download_file("BLE_STREAM_MOTION")

    def download_ble_stream_audio(self):
        """Download BLE_STREAM_AUDIO.wav file from S3"""
        return self.download_file("BLE_STREAM_AUDIO")

    def download_ble_stream_temperature(self):
        """Download BLE_STREAM_TEMPERATURE.wav file from S3"""
        return self.download_file("BLE_STREAM_TEMPERATURE")

    def download_ble_stream_voltage(self):
        """Download BLE_STREAM_VOLTAGE.wav file from S3"""
        return self.download_file("BLE_STREAM_VOLTAGE")

    def download_exam_video(self):
        """Download EXAM_VIDEO.mp4 file from S3"""
        return self.download_file("EXAM_VIDEO")

    def download_patient_tracking(self):
        """Download PATIENT_TRACKING.json file from S3"""
        return self.download_file("PATIENT_TRACKING")

    def download_exam_details(self):
        """Download EXAM_DETAILS.json file from S3"""
        return self.download_file("EXAM_DETAILS")

    def download_normalized_audio(self):
        """Download NORMALIZED.wav file from S3"""
        return self.download_file("NORMALIZED")

    def load_exam_details(self):
        """Load EXAM_DETAILS.json from S3 to local and parse it"""
        if not self.download_exam_details():
            return False
        try:
            with open("EXAM_DETAILS.json") as f:
                self.EXAM_DETAILS = json.load(f)
            return True
        except FileNotFoundError:
            logging.error("EXAM_DETAILS.json file not found")
        except json.JSONDecodeError:
            logging.error("Error decoding JSON from EXAM_DETAILS.json")
        return False

    def get_exam_details(self):
        """Get keys from the EXAM_DETAILS.json"""
        try:
            if self.EXAM_DETAILS is None:
                new_path = self.download_exam_details()
                if not new_path:
                    return None
                return new_path
            else:

                return self.EXAM_DETAILS
        except FileNotFoundError:
            logging.error("EXAM_DETAILS.json file not found")
            return None

    def get_key_value(self, key):
        """Get value for a specific key from EXAM_DETAILS.json"""
        if self.EXAM_DETAILS is None:
            if not self.load_exam_details():
                return None
        return self.EXAM_DETAILS
