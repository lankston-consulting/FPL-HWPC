from utils import singleton

class Names(singleton.Singleton):
    class Tables(singleton.Singleton):
        ids = 'ids'
        harvest = 'harvest_data'
        timber_products = 'timber_product_data'
        primary_products = 'primary_products'
        primary_product_ratios = 'primary_product_ratios'
        end_use_ratios = 'end_use_ratios'
        end_use_halflifes = 'end_use_products'
        discard_destinations = 'discard_destinations'
        discard_types = 'discard_types'
        discard_disposition_ratios = 'discarded_disposition_ratios'
        regions = 'regions'
        energy_capture = 'x_burned_energy_capture'
    
    class Fields(singleton.Singleton):

        #########################################
        ## Inputs
        #########################################

        id = 'ID'

        region_id = 'RegionID'
        region_name = 'Name'

        harvest_year = 'Year'
        ccf = 'ccf'
        ratio = 'Ratio'

        timber_product_id = 'TimberProductID'
        timber_product_ratio = 'TimberProductRatio'

        primary_product_id = 'PrimaryProductID'
        primary_product_ratio = 'PrimaryProductRatio'

        end_use_id = 'EndUseID'
        end_use_ratio = 'EndUseRatio'
        end_use_halflife = 'HalfLife'

        timber_product = 'TimberProduct'
        primary_product = 'PrimaryProduct'
        end_use_product = 'EndUseProduct'

        discard_type_id = 'DiscardTypeID' # paper and wood?
        discard_destination_id = 'DiscardDestinationID'
        discard_description = 'Description'
        discard_destination_ratio = 'DiscardDestinationRatio'

        landfill_fixed_ratio = 'LandfillFixedRatio'
        landfill_halflife = 'LandfillHalfLife'
        dump_halflife = 'DumpHalfLife'
        recycled_halflife = 'RecycledHalfLife'

        paper = 'paper'
        wood = 'wood'

        paper_halflife = 'PaperHalfLife'
        wood_halflife = 'WoodHalfLife'

        #########################################
        ## Results
        #########################################

        timber_product_results = 'timber_products'
        primary_product_results = 'primary_products'
        end_use_results = 'end_use'
        products_in_use = 'products_in_use'
        discarded_products_results = 'discarded_products'
        running_discarded_products = 'cum_discarded_products'
        discarded_products_adjusted = 'discarded_products_adjusted'
        discard_paper = 'discarded_paper'
        discard_wood = 'discarded_wood'
        discard_wood_paper = 'discarded_wood_or_paper'
        discard_dispositions = 'discard_dispositions'


        burned = 'Burned'
        recycled = 'Recycled'
        composted = 'Composted'
        landfills = 'Landfills'
        dumps = 'Dumps'

        can_decay = 'can_decay'
        decay_ratio = 'decay_ratio'
        running_can_decay = 'cum_can_decay'

        discard_remaining = 'discard_remaining'



