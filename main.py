from hwpc import model
from config import gch
import json
import os,shutil

if __name__ == '__main__':
    test = gch.download_file('hwpcarbon-data','hpwc-user-inputs/user_request_20210909_204340/user_input.json')
    f = open("utils/default_paths.json",)
    print(f)
    default_json = json.load(f)
    f.close()
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


    with open('data/inputs.json', 'w') as outfile:
        json.dump(inputs, outfile)

    for key,value in inputs.items():
        print(key,value)

    m = model.Model()
    m.run()
    print('done')
