from utils import singleton

class Names(singleton.Singleton):
    class Tables(singleton.Singleton):
        harvest = 'harvest_data'
        timber_products = 'timber_product_data'
        primary_product_ratios = 'primary_product_ratios'
        end_use_ratios = 'end_use_ratios'
    
    class Fields(singleton.Singleton):
        id = 'ID'

        harvest_year = 'Year'
        ccf = 'ccf'

        timber_product_id = 'TimberProductID'
        
        ratio = 'Ratio'

        primary_product_id = 'PrimaryProductID'