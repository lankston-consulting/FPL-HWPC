from utils import singleton

class Names(singleton.Singleton):
    class Tables(singleton.Singleton):
        ids = 'ids'
        harvest = 'harvest_data'
        timber_products = 'timber_product_data'
        primary_product_ratios = 'primary_product_ratios'
        end_use_ratios = 'end_use_ratios'
        end_use_halflifes = 'end_use_products'
        discard_destinations = 'discard_destinations'
        discard_types = 'discard_types'
        discard_disposition_ratios = 'discarded_disposition_ratios'
        regions = 'regions'
    
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

        discard_type_id = 'DiscardTypeID'
        discard_destination_id = 'DiscardDestinationID'
        discard_destination = 'Description'
        discard_destination_ratio = 'DiscardDestinationRatio'

        #########################################
        ## Results
        #########################################

        timber_product_results = 'timber_products_ccf'
        primary_product_results = 'primary_products_ccf'
        end_use_results = 'end_use_ccf'
        end_use_in_use = 'products_in_use'
        discarded_products_results = 'discarded_products_ccf'