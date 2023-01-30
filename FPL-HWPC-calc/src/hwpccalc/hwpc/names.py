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

        loss_factor = "end_use_loss_factor"

        timber_product_id = "TimberProductID"
        timber_product_ratio = "TimberProductRatio"

        primary_product_id = "PrimaryProductID"
        primary_product_ratio = "PrimaryProductRatio"

        end_use_id = "EndUseID"
        ratio_group = "RatioGroup"
        end_use_ratio = "EndUseRatio"
        end_use_halflife = "EndUseHalfLife"
        """The halflife or chi2 parameter of how long wood products are in use before discarding"""

        primary_product_ratio_direct = "PrimaryProductDirectRatio"
        end_use_ratio_direct = "EndUseDirectRatio"

        timber_product = "TimberProduct"
        """Timber product name"""
        primary_product = "PrimaryProduct"
        """Primary product name"""
        end_use_product = "EndUseProduct"
        """End use product name"""

        discard_type_id = "DiscardTypeID"  # paper and wood?
        """Wood or paper ID"""
        discard_destination_id = "DiscardDestinationID"
        discard_description = "Description"
        """Discard destination name"""
        discard_destination_ratio = "DiscardDestinationRatio"

        fixed_ratio = "FixedRatio"
        """Percent of discard to "fix", i.e. permanently sequestered"""
        halflife = "HalfLife"
        recovered = "recovered"
        fixed = "fixed"
        """Amount of carbon permanently sequestered"""

        paper = "paper"
        wood = "wood"

        paper_halflife = "PaperHalfLife"
        wood_halflife = "WoodHalfLife"

        fuel = "Fuel"
        conversion_factor = "ConversionFactor"

        #########################################
        ## Results
        #########################################

        timber_products = "timber_products"
        """Timber product results are raw materials created from harvest wood products"""
        primary_products = "primary_products"
        """Primary products are created from timber products and are general wood products"""
        end_use_products = "end_use"
        """End use products are specific wood products that can are ready to put into use"""
        end_use_available = "end_use_sum"
        """End use available are end use products after 'end use loss' is taken into accoutn"""
        products_in_use = "products_in_use"
        """End use products in use"""
        discarded_products = "discarded_products"
        """Products discarded from use in each year"""
        discarded_dispositions = "discarded_dispositions"
        """Discarded products in a discard destination"""

        paper_flag = "Paper"

        burned = "Burned"
        recycled = "Recycled"
        composted = "Composted"
        landfills = "Landfills"
        dumps = "Dumps"

        can_decay = "can_decay"
        """Amount of discarded material subject to decay. (Does not include fixed carbon)."""
        could_decay = "could_decay"
        """The running sum of can_decay, represents the total pool of materal that could decay
        as products are freshly discarded each year."""
        decay_rate = "decay_rate"

        discarded_remaining = "discarded_remaining"
        discarded_remaining_sum = "discarded_remaining_sum"

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
