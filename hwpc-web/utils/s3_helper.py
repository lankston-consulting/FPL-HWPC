import logging
import boto3
from botocore.exceptions import ClientError
import json
import tempfile
import os
import io
import zipfile


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
            response = S3Helper.s3_client.upload_fileobj(
                file_name, bucket, object_name, ExtraArgs={"ACL": "public-read"}
            )
        except ClientError as e:
            logging.error(e)
            return False
        return True

    @staticmethod
    def read_zipfile(bucket, file_name):

        obj = S3Helper.s3_resource.Object(bucket, file_name)
        contents = {}
        with io.BytesIO(obj.get()["Body"].read()) as tf:
            # rewind the file
            tf.seek(0)
            # Read the file as a zipfile and process the members
            with zipfile.ZipFile(tf, mode="r") as zipf:
                for subfile in zipf.namelist():
                    file_contents = zipf.read(subfile).decode("utf-8")
                    contents[subfile] = file_contents

        return contents

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
        print(bucket_name)
        print(source_file_name)
        data_json = {
            "scenario_name": "",
            "email": "",
            "user_string": "",
            "harvest_data_type": "",
            "is_official_record": "",
            "end_use_loss_factor": 0,
            "simulation_date": "",
            "start_year": 0,
            "end_year": 0,
            "region": {"name": "", "custom": "false"},
            "decay_function": "chi2",
            "monte_carlo": {"iterations": 1},
            "inputs": {
                "harvest_data.csv": "",
                "timber_product_ratios.csv": "",
                "timber_products.csv": "",
                "id_lookup.csv": "",
                "primary_products.csv": "",
                "primary_product_ratios.csv": "",
                "parameters.csv": "",
                "end_use_product_ratios.csv": "",
                "end_use_products.csv": "",
                "discard_destinations.csv": "",
                "discard_destination_ratios.csv": "",
                "distribution_parameters.csv": "",
                "regions.csv": "",
                # "distribution_data.csv": "",
                "discard_burned_w_energy_capture.csv": "",
                "mbf_to_ccf_conversion.csv": "",
            },
        }
        # Code parses through data pulled from web
        for key, value in data.items():
            # If the code was potentially converted from a pandas dataframe for wide-to-long formatting or is just a string type it pases through here
            print(key)

            if (
                str(type(value)) == "<class 'str'>"
                and ".csv" in key
                and "primary_product_ratios" not in key
            ):

                path = source_file_name + key
                temp_file = tempfile.TemporaryFile()
                temp_file.write(value.encode())
                temp_file.seek(0)
                data_json["inputs"][key] = path

                S3Helper.upload_file(temp_file, bucket_name, path)
                temp_file.close()
            if (
                str(type(value)) == "<class 'str'>"
                and ".csv" not in key
                and "iterations" not in key
                and "region" not in key
            ):
                data_json[key] = value
            if (
                str(type(value)) == "<class 'str'>"
                and ".csv" not in key
                and "iterations" in key
            ):
                data_json["monte_carlo"][key] = value
            if (
                str(type(value)) == "<class 'str'>"
                and ".csv" not in key
                and "region" in key
            ):
                data_json["region"]["name"] = value
                if value == "Custom":
                    data_json["region"]["custom"] = "true"

            # If the input is not empty, it will make the file and upload. If it is empty, it will be skipped and save memory.
            if (
                str(type(value)) == "<class 'werkzeug.datastructures.FileStorage'>"
                and ".csv" in key
            ):
                if value.content_length == "text/csv":
                    path = source_file_name + key
                    temp_file = tempfile.TemporaryFile()
                    temp_file.write(value.read())
                    temp_file.seek(0)
                    data_json["inputs"][key] = path
                    S3Helper.upload_file(temp_file, bucket_name, path)
                    temp_file.close()
                # path = source_file_name+key
                # data_json[key]=path

        if data_json["region"]["custom"] == "false":
            data_json["inputs"]["primary_product_ratios.csv"] = ""

        else:
            path = source_file_name + "primary_product_ratios.csv"
            temp_file = tempfile.TemporaryFile()
            temp_file.write(data["primary_product_ratios.csv"].encode())
            temp_file.seek(0)
            data_json["inputs"]["primary_product_ratios.csv"] = path
            S3Helper.upload_file(temp_file, bucket_name, path)
            temp_file.close()

        for i in data_json["inputs"]:
            if data_json["inputs"][i] == "":
                data_json["inputs"][i] = "Default Data"
        print(data_json)
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
