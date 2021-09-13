from config import gch
import json
import os,shutil

class Input_Download(object):

    def __init__(self) -> None:
        super().__init__()

    def downloads(self):
        test = gch.download_file('hwpcarbon-data','hpwc-user-inputs/user_request_20210909_161047/user_input.json')

        with open("utils/default_paths.json", "r") as readjson:
            default_json = json.load(readjson)
        filled = test.read()
        filled = json.loads(filled)
        test.close()
        inputs = {}

        for default_key,default_value in default_json.items():
            if(default_key in filled):
                data_path = "data/"+default_key+".csv"
                file_path = filled[default_key]
                gch.download_blob('hwpcarbon-data',file_path,data_path)
                inputs[default_key] = data_path
            else:
                inputs[default_key] = "data/"+default_key+".csv"
                shutil.copy(default_value, 'data')

        for filled_key,filled_value in filled.items():
            if(filled_key not in inputs):
                data_path = "data/"+filled_key
                file_path = filled[filled_key]
                inputs[filled_key] = data_path
                gch.download_blob('hwpcarbon-data',file_path,data_path)

        with open('data/inputs.json', 'w') as outfile:
            json.dump(inputs, outfile)

        for key,value in inputs.items():
            print(key,value)
        print('done')