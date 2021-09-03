from utils import singleton

class Names(singleton.Singleton):
    class Tables(singleton.Singleton):
        ids = 'ids'
        harvest = 'harvest_data'
        timber_products = 'timber_product_data'
        primary_product_ratios = 'primary_product_ratios'
        end_use_ratios = 'end_use_ratios'
        end_use_halflifes = 'end_use_products'
        regions = 'regions'
    
    class Fields(singleton.Singleton):
        id = 'ID'

        region_name = 'Name'

        harvest_year = 'Year'
        ccf = 'ccf'
        ratio = 'Ratio'

        timber_product_id = 'TimberProductID'
        timber_product_ratio = 'TimberProductRatio'

        primary_product_id = 'PrimaryProductID'
        primary_product_ratio = 'PrimaryProductRatio'

        end_use_id = 'EndUseID'

        timber_product = 'TimberProduct'
        primary_product = 'PrimaryProduct'
        end_use_product = 'EndUseProduct'

        #########################################
        ## Results
        #########################################

        timber_product_results = 'timber_products_ccf'
        primary_product_results = 'primary_products_ccf'