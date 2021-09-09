from google.cloud import storage
import tempfile
from utils.data_loader import DataLoader


class UserData(DataLoader):
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
            cls._instance = super(UserData, cls).__new__(cls)

            if 'use_service_account' in kwargs:
                gcs_account = kwargs['use_service_account']
                cls._client = storage.Client.from_service_account_json(gcs_account['keyfile'])
            else:
                cls._client = storage.Client()
        return cls._instance
    
    @staticmethod
    def download_file(bucket, remote_path):
        """
        Download a file from GCS and write it to a temporary file on disk. Return the named
        temporary file.
        :param bucket:
        :param remote_path:
        :return:
        """
        bucket = UserData._client.bucket(bucket)
        blob = bucket.blob(remote_path)

        fp = tempfile.NamedTemporaryFile()

        UserData._client.download_blob_to_file(blob, fp)
        fp.seek(0)
        return fp

    def download_blob(bucket_name, remote_path, destination_file_name):
        """Downloads a blob from the bucket."""
        # The ID of your GCS bucket
        # bucket_name = "your-bucket-name"

        # The ID of your GCS object
        # source_blob_name = "storage-object-name"

        # The path to which the file should be downloaded
        # destination_file_name = "local/path/to/file"

        bucket = UserData._client.bucket(bucket_name)

        # Construct a client side representation of a blob.
        # Note `Bucket.blob` differs from `Bucket.get_blob` as it doesn't retrieve
        # any content from Google Cloud Storage. As we don't need additional data,
        # using `Bucket.blob` is preferred here.
        blob = bucket.blob(remote_path)
        blob.download_to_filename(destination_file_name)
