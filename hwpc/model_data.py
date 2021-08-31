from utils import data_reader
import json

class ModelData(object):
    
    _instance = None

    data = dict()

    def __new__(cls, *args, **kwargs):
        """Singleton catcher

        Returns:
            ModelData: The singleton ModelData object
        """
        if cls._instance is None:
            cls._instance = super(ModelData, cls).__new__(cls)
            dr = data_reader.DataReader()

            with open('utils/default_paths.json') as f:
                j = json.load(f)
                p = j['discard_destinations']
                val = dr.ReadFile(p)
            val = None

            cls.data = val

        return cls._instance

    
    def UpdateValues(vals: dict) -> None:
        """Update the internal lookup table for discard destinations. This should probably never be used

        Args:
            vals (dict): A dictionary of {'id':List, 'discard destinations':List}

        Returns:
            None
        """
        return None