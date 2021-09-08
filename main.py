from hwpc import model
from config import gch
import json
import os,shutil

if __name__ == '__main__':
    # m = model.Model()
    # m.run()

    # defaults = {
    #         "ccf_to_metric_tons_carbon":"./default_data/ccf_to_metric_tons_carbon.csv",
    #         "discard_burned_w_energy_capture":"./default_data/discard_burned_with_energy_capture.csv",
    #         "discard_destinations":"./default_data/discard_destinations.csv",
    #         "discard_half_lives":"./default_data/discard_half_lives.csv",
    #         "discard_ratios":"./default_data/discard_ratios.csv",
    #         "discard_types":"./default_data/discard_types.csv",
    #         "discarded_disposition_ratios":"./default_data/discarded_disposition_ratios.csv",
    #         "distribution_parameters.csv":"./default_data/distribution_parameters.csv",
    #         "end_use_half_lives":"./default_data/end_use_half_lives.csv",
    #         "end_use_product_ratios":"./default_data/end_use_product_ratios.csv",
    #         "end_use_products":"./default_data/end_use_products.csv",
    #         "end_use_ratios":"./default_data/end_use_ratios.csv",
    #         "id_lookup":"./default_data/id_lookup.csv",
    #         "mbf_to_ccf_conversion":"./default_data/mbf_to_ccf_conversion.csv",
    #         "parameters":"./default_data/parameters.csv",
    #         "primary_product_ratios":"./default_data/primary_product_ratios.csv",
    #         "primary_products":"./default_data/primary_products.csv",
    #         "regions":"./default_data/regions.csv",
    #         "timber_products":"./default_data/timber_products.csv",
    #         "x_burned_energy_capture":"./default_data/x_burned_energy_capture.csv"
    #         }

    test = gch.download_file('hwpcarbon-data','hpwc-user-inputs/user_request_20210908_161903/user_input.json')
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
    print('done')
