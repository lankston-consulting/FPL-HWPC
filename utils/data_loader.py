from abc import ABC, abstractmethod
import tempfile

class DataLoader(ABC):
    _client = None
    _instance = None

    def __new__(cls, *args, **kwargs):
        """Singleton catcher

        Returns:
            DiscardDestinations: The singleton DiscardDestinations object
        """
        if cls._instance is None:
            cls._instance = super(DataLoader, cls).__new__(cls)

        return cls._instance

    @abstractmethod
    def download_file(path: str) -> tempfile.TemporaryFile:
        """Abstract method for downloading a file from a cloud location

        Args:
            path: A reasonable path name that the cloud service will understand

        Returns:
            tempfile.TemporaryFile: An active temporary file object
        """

        return None
    
    @abstractmethod
    def download_blob(path: str):

        """Abstract method for dowloanding files and saving them to data folder

        Args:
            path: A reasonable path name that the cloud service will understand

        Returns:
            None
        """

        return None
    
    @abstractmethod
    def upload_blob(path: str):

        """Abstract method for uploading files to the cloud for front end use.

        Returns:
            path: A reasonable path name that the cloud service will understand
        """

        return None

