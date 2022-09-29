from hwpccalc.utils import singleton


class Names(singleton.Singleton):
    class Tables(singleton.Singleton):
        energy_capture = "discard_burned_with_energy_capture"
        discard_destination_ratios = "discard_destination_ratios"
        discard_destinations = "discard_destinations"
        discard_types = "discard_types"
        end_use_products = "end_use_products"
        end_use_product_ratios = "end_use_product_ratios"
        harvest = "harvest_data"
        harvest_data_type = "harvest_data_type"
        ids = "id_lookup"
        loss_factor = "loss_factor"
        mbf_conversion = "mbf_to_ccf_conversion"
        primary_product_ratios = "primary_product_ratios"
        primary_products = "primary_products"
        region = "region"
        regions = "regions"
        timber_products_ratios = "timber_product_ratios"
        timber_products = "timber_products"

    class Fields(singleton.Singleton):

        #########################################
        ## Inputs
        #########################################

        id = "ID"

        region_id = "RegionID"
        region_name = "Name"

        harvest_year = "Year"
        ccf = "ccf"
        mbf = "mbf"
        ratio = "Ratio"

        timber_product_id = "TimberProductID"
        timber_product_ratio = "TimberProductRatio"
        percent_burned = "PercentBurned"

        primary_product_id = "PrimaryProductID"
        primary_product_ratio = "PrimaryProductRatio"

        end_use_id = "EndUseID"
        ratio_group = "RatioGroup"
        end_use_ratio = "EndUseRatio"
        end_use_halflife = "EndUseHalfLife"

        primary_product_ratio_direct = "PrimaryProductDirectRatio"
        end_use_ratio_direct = "EndUseDirectRatio"

        timber_product = "TimberProduct"
        primary_product = "PrimaryProduct"
        end_use_product = "EndUseProduct"

        discard_type_id = "DiscardTypeID"  # paper and wood?
        discard_destination_id = "DiscardDestinationID"
        discard_description = "Description"
        discard_destination_ratio = "DiscardDestinationRatio"

        fixed_ratio = "FixedRatio"
        halflife = "HalfLife"
        recovered = "recovered"
        fixed = "fixed"

        paper = "paper"
        wood = "wood"

        paper_halflife = "PaperHalfLife"
        wood_halflife = "WoodHalfLife"

        fuel = "Fuel"
        conversion_factor = "ConversionFactor"

        #########################################
        ## Results
        #########################################

        timber_product_results = "timber_products"
        primary_product_results = "primary_products"
        primary_product_sum = "primary_products_sum"
        end_use_results = "end_use"
        end_use_sum = "end_use_sum"
        products_in_use = "products_in_use"
        discarded_products_results = "discarded_products"
        discarded_in_year = "discarded_in_year"
        discard_dispositions_in_year = "discard_dispositions_in_year"
        discard_dispositions = "discard_dispositions"

        paper_flag = "Paper"

        burned = "Burned"
        recycled = "Recycled"
        composted = "Composted"
        landfills = "Landfills"
        dumps = "Dumps"

        # new_decay = 'new_decay'
        can_decay = "can_decay"
        could_decay = "could_decay"
        decay_rate = "decay_rate"
        running_can_decay = "can_decay_cumsum"

        discard_remaining = "discard_remaining"
        discard_remaining_sum = "discard_remaining_sum"

        emitted = "emitted"
        emitted_all = "all_emitted"
        present = "present"

        burned_with_energy_capture = "burned_w_energy_capture"
        burned_wo_energy_capture = "burned_wo_energy_capture"

        emitted_with_energy_capture = "emitted_w_energy_capture"
        emitted_wo_energy_capture = "emitted_wo_energy_capture"

        accounted = "accounted"
        error = "error"

        carbon = "mgc"
        co2e = "co2e"

        swds = "SWDS"

        def c(name):
            return name + "_" + Names.Fields.carbon

        def change(name):
            return name + "_" + "change"

        def mgc(name):
            return name + "_" + Names.Fields.carbon

        def co2(name):
            return name + "_" + Names.Fields.co2e

        def ppresent(name):
            return name + "_" + Names.Fields.present

        def eemitted(name):
            return name + "_" + Names.Fields.emitted

    class Output(singleton.Singleton):
        input_path = ""
        output_path = ""
        run_name = ""
        scenario_info = ""
