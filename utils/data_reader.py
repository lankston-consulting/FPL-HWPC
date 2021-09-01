from tempfile import TemporaryFile
import pandas

class DataReader(object):

    def __init__(self) -> None:
        super().__init__()

    def read_file(self, path: object) -> pandas.DataFrame:
        """Read a csv or file object into a pandas DataFrame

        Args:
            path: Either a path to a local file location (probably in /data) or an open file connection

        Raises:
            ValueError: If the passed object is not the correct type

        Returns:
            pandas.DataFrame: A DataFrame representation of the input file
        """
        f = pandas.read_csv(path)
        return f
        # if path is str or path is TemporaryFile:
        #     f = pandas.read_csv(data=path)
        #     return f
        # else:
        #     raise ValueError('path should be a string to a local location or an active file object')
    