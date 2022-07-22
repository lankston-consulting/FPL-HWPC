import json
import os
import shutil

from dotenv import load_dotenv

from config import gch

from hwpc.names import Names as nm

load_dotenv()


class InputDownload(object):
    def __init__(self) -> None:
        super().__init__()
        self.bucket = os.getenv("GCP_BUCKET")
        if self.bucket is None:
            self.bucket = "hwpcarbon-data"

    def downloads(self):
        if not os.path.exists("data"):
            os.makedirs("data")

        with (
            gch.download_temp(self.bucket, nm.Output.output_path + "/user_input.json")
        ) as online_data:

            with open("utils/default_paths.json", "r") as readjson:
                default_json = json.load(readjson)

                filled = online_data.read()
                filled = json.loads(filled)

                inputs = {}

                for default_key, default_value in default_json.items():
                    if default_key in filled:
                        # print("filled "+default_key)
                        data_path = "data/" + default_key
                        file_path = filled[default_key]
                        gch.download_blob(self.bucket, file_path, data_path)
                        inputs[default_key] = data_path
                    else:
                        # print("not filled " + default_key)
                        inputs[default_key] = "data/" + default_key
                        shutil.copy(default_value, "data")

                for filled_key, filled_value in filled.items():
                    if filled_key not in inputs:
                        # print("final filled: " + filled_key)
                        data_path = "data/" + filled_key
                        file_path = filled[filled_key]
                        inputs[filled_key] = data_path
                        gch.download_blob(self.bucket, file_path, data_path)

                with open("data/inputs.json", "w") as outfile:
                    json.dump(inputs, outfile)

                # for key, value in inputs.items():
                #     print(key, value)

        print("data loaded")
