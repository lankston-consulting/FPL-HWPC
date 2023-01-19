from abc import ABC, abstractmethod
from google.cloud import storage
import tempfile
import datetime
import json


class StorageHelper(ABC):
    """
    Singleton object for working with GCS objects.
    """

    _client = None
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Singleton catcher. Can optionally pass a kwarg or "use_service_account" with a value of
        {'keyfile'=path_to_json_keyfile} to authenticate as a service account
        :param args:
        :param kwargs:
        """
        if cls._instance is None:
            cls._instance = super(StorageHelper, cls).__new__(cls)

        return cls._instance

    @abstractmethod
    def check_file_exists_on_cloud(self, bucket, filename):
        """
        Pass a bucket and a filename (including any prefix path
        and return whether it exists on cloud storage
        :param bucket: Bucket name
        :param filename: A path and filename to the file in the bucket
        :return: Boolean, exists or not
        """
        pass

    @abstractmethod
    def list_blobs(self, bucket_name, p=""):
        """
        Return a list of all object blobs in the given bucket matching the optional prefix p
        :param bucket_name:
        :param p:
        :return:
        """
        pass

    @abstractmethod
    def list_blobs_names(self, bucket_name, p=""):
        """
        Return a list of all blob names in the given bucket matching the optional prefix p
        :param bucket_name:
        :param p:
        :return:
        """
        pass

    @abstractmethod
    def download_temp(self, bucket, remote_path):
        """
        Download a file from GCS and write it to a temporary file on disk. Return the named
        temporary file.
        :param bucket:
        :param remote_path:
        :return:
        """
        pass

    @abstractmethod
    def download_blob(self, bucket, remote_path, local_path):
        """
        Download a file from GCS and write it to disk.
        :param bucket:
        :param remote_path:
        :return:
        """
        pass

    @abstractmethod
    def upload_temp(self, bucket_name, source_file_obj, destination_blob_name):
        """
        Upload a file object from disk. Works with temp files, should also work with "real" files as long
        as they're open as a file object. TODO test real files
        :param bucket_name: Bucket to upload file to
        :param source_file_obj: An active file object to upload
        :param destination_blob_name: A name, including any "subdirectories", to upload the blob to (but not bucket)
        :return:
        """

        pass

    @abstractmethod
    def delete_blob(self, bucket_name, blob_name):
        """Deletes a blob from the bucket."""

        pass

    @abstractmethod
    def move_blob(self, source_bucket, source_blob_name, dest_bucket, dest_blob_name):
        """

        :param source_bucket:
        :param source_blob_name:
        :param dest_bucket:
        :param dest_blob_name:
        :return:
        """
        pass

    @abstractmethod
    def upload_input_group(self, bucket_name, source_file_name, data, data_type):
        """[summary]

        Args:
            bucket_name ([type]): [description]
            source_file_name ([type]): [description]
            data ([type]): [description]
            data_type ([type]): [description]
        """

        pass
