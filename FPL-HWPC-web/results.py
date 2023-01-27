import datetime
import json
from config import gch


class Results:
    def __init__(self, file_group):
        self.bucket = "hwpcarbon-data"
        self.prefix = file_group
        self.basic_path = (
            "https://storage.googleapis.com/" + self.bucket + "/" + self.prefix + "/"
        )
        self._set_file_collection()

    def _set_file_collection(self):
        blobs = gch.list_blobs_names(self.bucket, self.prefix)
        f_col = dict()
        counter = 0
        for b in blobs:
            f_col[counter].append(b)
            counter += 1
            print(f_col)

        self.f_col = f_col

    def file_collection(self):
        """
        Last-chance catcher for an uninstantiated file colleciton instance
        :return:
        """
        if self.f_col is None:
            self._set_file_collection()

        f_list = self.f_col
        return f_list
