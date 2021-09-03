from utils import singleton

class Names(singleton.Singleton):
    class Tables(singleton.Singleton):
        harvest = 'harvest_data'
        timber_products = 'timber_product_data'
        primary_product_ratios = 'primary_product_ratios'
        end_use_ratios = 'end_use_ratios'
    
    class Fields(singleton.Singleton):
        harvest_year = 'Year'
        timber_product_id = 'Timber Product ID'
        ccf = 'ccf'
        ratio = 'Ratio'