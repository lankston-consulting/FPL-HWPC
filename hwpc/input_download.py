import json
import os
import shutil
from config import gch

class InputDownload(object):

    def __init__(self) -> None:
        super().__init__()

    def downloads(self, path):
        if not os.path.exists('data'):
            os.makedirs('data')

        with (gch.download_file('hwpcarbon-data', path)) as online_data:

            with open("utils/default_paths.json", "r") as readjson:
                default_json = json.load(readjson)
            
                filled = online_data.read()
                filled = json.loads(filled)
                
                inputs = {}

                for default_key, default_value in default_json.items():
                    if(default_key in filled):
                        data_path = "data/" + default_key + ".csv"
                        file_path = filled[default_key]
                        gch.download_blob('hwpcarbon-data', file_path,data_path)
                        inputs[default_key] = data_path
                    else:
                        inputs[default_key] = "data/" + default_key + ".csv"
                        shutil.copy(default_value, 'data')

                for filled_key,filled_value in filled.items():
                    if filled_key not in inputs:
                        data_path = "data/" + filled_key
                        file_path = filled[filled_key]
                        inputs[filled_key] = data_path
                        gch.download_blob('hwpcarbon-data', file_path,data_path)

                with open('data/inputs.json', 'w') as outfile:
                    json.dump(inputs, outfile)

                for key, value in inputs.items():
                    print(key, value)

        print('done')