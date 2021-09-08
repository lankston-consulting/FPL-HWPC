#from hwpc import model
from config import gch
import json

if __name__ == '__main__':
    # m = model.Model()
    # m.run()

    defaults = {
            "ccf_to_metric_tons_carbon":"./default_data/ccf_to_metric_tons_carbon.csv",
            "discard_burned_w_energy_capture":"./default_data/discard_burned_with_energy_capture.csv",
            "discard_destinations":"./default_data/discard_destinations.csv",
            "discard_half_lives":"./default_data/discard_half_lives.csv",
            "discard_ratios":"./default_data/discard_ratios.csv",
            "discard_types":"./default_data/discard_types.csv",
            "discarded_disposition_ratios":"./default_data/discarded_disposition_ratios.csv",
            "distribution_parameters.csv":"./default_data/distribution_parameters.csv",
            "end_use_half_lives":"./default_data/end_use_half_lives.csv",
            "end_use_product_ratios":"./default_data/end_use_product_ratios.csv",
            "end_use_products":"./default_data/end_use_products.csv",
            "end_use_ratios":"./default_data/end_use_ratios.csv",
            "id_lookup":"./default_data/id_lookup.csv",
            "mbf_to_ccf_conversion":"./default_data/mbf_to_ccf_conversion.csv",
            "parameters":"./default_data/parameters.csv",
            "primary_product_ratios":"./default_data/primary_product_ratios.csv",
            "primary_products":"./default_data/primary_products.csv",
            "regions":"./default_data/regions.csv",
            "timber_products":"./default_data/timber_products.csv",
            "x_burned_energy_capture":"./default_data/x_burned_energy_capture.csv"
            }

    test = gch.download_file('hwpcarbon-data','hpwc-user-inputs/user_request_20210907_123956/user_input.json')
    filled = test.read()
    filled = json.loads(filled)
    test.close()
    inputs = {}
    print(filled)
    for key,value in filled.items():
        if(key in defaults):
            inputs[key] = gch.download_file('hwpcarbon-data',value)
        else:
            inputs[key] = gch.download_file('hwpcarbon-data',value)
            for default_key,default_value in defaults.items():
                inputs[default_key] = default_value


    for i in inputs:
        print(i)
    print('done')
