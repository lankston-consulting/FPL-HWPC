from abc import ABC
import tempfile

class DataLoader(ABC):

    _instance = None

    def __init__(self) -> None:
        super().__init__()

    def __new__(cls, *args, **kwargs):
        """Singleton catcher

        Returns:
            DiscardDestinations: The singleton DiscardDestinations object
        """
        if cls._instance is None:
            cls._instance = super(DataLoader, cls).__new__(cls)

        return cls._instance

    def DownloadFile(path: str) -> tempfile.TemporaryFile:
        """Abstract method for downloading a file from a cloud location

        Args:
            path: A reasonible path name that the cloud service will understand

        Returns:
            tempfile.TemporaryFile: An active temporary file object
        """

        return None
    