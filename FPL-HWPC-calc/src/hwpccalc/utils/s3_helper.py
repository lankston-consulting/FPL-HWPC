import json
import logging
import os
import tempfile

import boto3
from botocore.exceptions import ClientError

import hwpccalc.config


class S3Helper(object):
    service_id = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

    # We use s3_client to upload data to the bucket with our service account
    s3_client = boto3.client(
        "s3", aws_access_key_id=service_id, aws_secret_access_key=secret_key
    )

    # We use s3_resource to download data from the bucket with our service account
    s3_resource = boto3.resource(
        "s3", aws_access_key_id=service_id, aws_secret_access_key=secret_key
    )

    @staticmethod
    def upload_file(file_name, bucket, object_name=None):
        """Upload a file to an S3 bucket

        :param file_name: File to upload
        :param bucket: Bucket to upload to
        :param object_name: S3 object name. If not specified then file_name is used
        :return: True if file was uploaded, else False
        """

        # If S3 object_name was not specified, use file_name
        if object_name is None:
            object_name = os.path.basename(file_name)

        # Upload the file

        try:
            S3Helper.s3_client.upload_fileobj(file_name, bucket, object_name)
        except ClientError as e:
            logging.error(e)
            return False
        return True

    @staticmethod
    def download_file(bucket, file_name):
        s3_bucket = S3Helper.s3_resource.Bucket(bucket)
        fp = tempfile.NamedTemporaryFile()
        s3_bucket.download_fileobj(file_name, fp)
        fp.seek(0)
        return fp

    @staticmethod
    def upload_input_group(bucket_name: str, source_file_name: str, data: dict) -> None:
        """[summary]
        This helper function that uploads a data cluster of user inputs to a unique folder, likely named with a user generated hash id.
        This function is specially modified and used in hwpc-web
        Args:
            bucket_name ([type]): The name of the destination bucket you are uploading to.
            source_file_name ([type]): The name of the destination folder for the user date, this consists of "hwpc-user-inputs" and the user's generated id.
            data ([type]): The data to be delivered to the destination folder.
            data_type ([type]): A logic check for harvested_wood_products.
        """
        data_json = {}
        # Code parses through data pulled from web
        for key, value in data.items():
            # If the code was potentially converted from a pandas dataframe for wide-to-long formatting or is just a string type it pases through here
            if str(type(value)) == "<class 'str'>":
                path = source_file_name + key
                temp_file = tempfile.TemporaryFile()
                temp_file.write(value.encode())
                temp_file.seek(0)
                data_json[key] = path

                S3Helper.upload_file(temp_file, bucket_name, path)
                temp_file.close()
            # If the input is not empty, it will make the file and upload. If it is empty, it will be skipped and save memory.
            if str(type(value)) == "<class 'werkzeug.datastructures.FileStorage'>":
                if value.content_length == "text/csv":
                    path = source_file_name + key
                    temp_file = tempfile.TemporaryFile()
                    temp_file.write(value.read())
                    temp_file.seek(0)
                    data_json[key] = path
                    S3Helper.upload_file(temp_file, bucket_name, path)
                    temp_file.close()
                path = source_file_name + key
                data_json[key] = path

        # The json of all the file paths is converted into a string then to bytes to be uploaded as a temp file for use in the worker.
        data_json = json.dumps(data_json)
        data_json = data_json.encode()
        user_file = tempfile.TemporaryFile()
        user_file.write(data_json)
        user_file.seek(0)
        S3Helper.upload_file(
            user_file, bucket_name, source_file_name + "user_input.json"
        )
        user_file.close()
        return
