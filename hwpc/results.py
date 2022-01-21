from io import BytesIO
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json
import os
import tempfile
import zipfile
import zlib

from config import gch
from hwpc import model_data
from hwpc.names import Names as nm
from utils import pickler



class Results(pickler.Pickler):

    def __init__(self) -> None:
        super().__init__()

        self.harvest_data = None
        self.timber_products_data = None
        self.primary_products_data = None
        """ Pre-aggregated and melted user inputs
        """

        self.harvests = None
        """Level 0, simply the annual harvest amount
        """

        self.timber_products = None
        """Level 1 products. timber_products is a direct ratio-driven calculation
        of the various timber products created from annual harvest
        """

        self.primary_products = None
        """Level 2 products. A direct ratio driven calculation from timber products
        """

        self.end_use_products = None
        """Level 3 products. For each primary product, directly calculate the end uses
        """

        self.products_in_use = None
        """Level 4 product. Using a cumulative decay, sort end use products into "in use"
        and "discarded in year"
        """
        
        self.discarded_products = None
        """Level 5 product. From products in use in this year, distribute discards into 
        applicable pools via discard destination ratios
        """

        self.dispositions = None
        """Level 6, final discard product. Allow discarded products to decay (then emit) and
        add new products into the remaining pool. Repeat over subsequent years.
        """

        self.working_table = None

        self.total_dispositions = None

        self.fuelwood = None

        self.burned_wo_energy_capture = None

        self.burned_w_energy_capture = None
        
        # Final output collections
        self.annual_timber_products = None
        """Filtered end results, giving primary products in units of carbon
        """

        self.burned = None
        """Aggregated burned dispositions, which are emissions by year
        """
        self.composted = None
        """Aggregated compost dispositions, which are emissions by year
        """
        
        self.recovered_in_use = None
        """Recovered products in use 
        """
        self.in_landfills = None
        self.in_dumps = None
        self.fuelwood = None
        
        self.emissions = None
        """Deprecated. Emissions should now be retrieved from either the 
        all_emitted table ot the total_all_dispositions
        """
        
        self.all_in_use = None
        """All products in use, aggregated by destination, disposition, and year.
        Includes products in use, recycled, and present in SWDS
        """

        self.all_emitted = None
        """Similiar to all_in_use, but contains all values of emissions
        """

        self.final = None
        """TODO
        """

        self.total_all_dispositions = None

        self.big_table = None

        ##################################

        self.md = model_data.ModelData()
    
        self.zip_buffer = BytesIO()
        
        self.zip = zipfile.ZipFile(self.zip_buffer, mode='w', compression=zipfile.ZIP_STORED, allowZip64=False)
        
        self.captions = {}

        

        return

    def save_output(self):
        self.save_user_inputs()
        self.save_results()
        self.save_total_dispositions()

    def save_user_inputs(self):
        harvest_data = pd.DataFrame(self.harvest_data)
        timber_products_data = pd.DataFrame(self.timber_products_data)
        primary_products_data = pd.DataFrame(self.primary_products_data)
        with tempfile.TemporaryFile() as temp:
            harvest_data.to_csv(temp)
            temp.seek(0)
            self.zip.writestr('harvest_data.csv', temp.read(), compress_type=zipfile.ZIP_STORED)
        
        with tempfile.TemporaryFile() as temp:
            timber_products_data.to_csv(temp)
            temp.seek(0)
            self.zip.writestr('timber_products_data.csv', temp.read(), compress_type=zipfile.ZIP_STORED)

        with tempfile.TemporaryFile() as temp:
            primary_products_data.to_csv(temp)
            temp.seek(0)
            self.zip.writestr('primary_products_data.csv', temp.read(), compress_type=zipfile.ZIP_STORED)

        return

    def save_results(self):
        with tempfile.TemporaryFile() as temp:
            self.working_table.to_csv(temp)
            temp.seek(0)
            self.zip.writestr('results.csv', temp.read(), compress_type=zipfile.ZIP_STORED)
        return
        
    def save_total_dispositions(self):
        results_json = {}
        

        final = pd.DataFrame(self.final)
        primary_products = pd.DataFrame(self.primary_products)
        total_in_use = pd.DataFrame(self.all_in_use)
        total_all_dispositions = pd.DataFrame(self.total_all_dispositions)
        annual_timber_products = pd.DataFrame(self.annual_timber_products)
        big_table = pd.DataFrame(self.big_table)
        burned_w_energy_capture = pd.DataFrame(self.burned_w_energy_capture)
        burned_wo_energy_capture = pd.DataFrame(self.burned_wo_energy_capture)

        P = nm.Fields.ppresent
        E = nm.Fields.eemitted
       

        # CUMULATIVE DISCARDED PRODUCTS
        cum_products = total_all_dispositions[[nm.Fields.harvest_year,nm.Fields.co2(nm.Fields.products_in_use)]]
        self.generate_graph(cum_products,
                        cum_products[nm.Fields.co2(nm.Fields.products_in_use)],
                        total_all_dispositions[nm.Fields.harvest_year],
                        0.5,
                        'Total Cumulative Carbon in End Use Products in Use',
                        'Total cumulative metric tons carbon stored in end-use products in use manufactured from total timber harvested from ' + str(total_all_dispositions[nm.Fields.harvest_year].min()) + ' to ' + str(total_all_dispositions[nm.Fields.harvest_year].max()) + '. The recalcitrance of carbon in harvested wood products is highly dependent upon the end use of those products. The carbon remaining in the end-use products in use pool in a given inventory year includes products in use and recovered products. Carbon emissions are displayed in units of carbon dioxide equivalent (CO2e) and do not include other carbon-based greenhouse gases such as methane.',
                        'total_end_use_products',
                        'Metric Tons CO2e')
        
        self.generate_graph_no_caption(cum_products,
                        cum_products[nm.Fields.co2(nm.Fields.products_in_use)],
                        total_all_dispositions[nm.Fields.harvest_year],
                        0.5,
                        'Total Cumulative Carbon in End Use Products in Use',
                        'Total cumulative metric tons carbon stored in end-use products in use manufactured from total timber harvested from ' + str(total_all_dispositions[nm.Fields.harvest_year].min()) + ' to ' + str(total_all_dispositions[nm.Fields.harvest_year].max()) + '. The recalcitrance of carbon in harvested wood products is highly dependent upon the end use of those products. The carbon remaining in the end-use products in use pool in a given inventory year includes products in use and recovered products. Carbon emissions are displayed in units of carbon dioxide equivalent (CO2e) and do not include other carbon-based greenhouse gases such as methane.',
                        'total_end_use_products',
                        'Metric Tons CO2e')

        # CUMULATIVE  PRESENT RECOVERED PRODUCTS CARBON CO2E
        recycled_carbon = total_all_dispositions[[nm.Fields.harvest_year,nm.Fields.co2(P(nm.Fields.recycled))]]
        self.generate_graph(recycled_carbon,
                        recycled_carbon[nm.Fields.co2(P(nm.Fields.recycled))],
                        total_all_dispositions[nm.Fields.harvest_year],
                        0.3,
                        'Total Cumulative Carbon in Recovered Products in Use',
                        'Total cumulative metric tons carbon stored in recovered products in use manufactured from total timber harvested from ' + str(total_all_dispositions[nm.Fields.harvest_year].min()) + ' to ' + str(total_all_dispositions[nm.Fields.harvest_year].max()) + '. Carbon in recovered products in use are recycled wood and paper that reenters the products in use category. Carbon emissions are displayed in units of carbon dioxide equivalent (CO2e) and do not include other carbon-based greenhouse gases such as methane.',
                        'total_recycled_carbon_co2e',
                        'Metric Tons CO2e')
        
        self.generate_graph_no_caption(recycled_carbon,
                        recycled_carbon[nm.Fields.co2(P(nm.Fields.recycled))],
                        total_all_dispositions[nm.Fields.harvest_year],
                        0.3,
                        'Total Cumulative Carbon in Recovered Products in Use',
                        'Total cumulative metric tons carbon stored in recovered products in use manufactured from total timber harvested from ' + str(total_all_dispositions[nm.Fields.harvest_year].min()) + ' to ' + str(total_all_dispositions[nm.Fields.harvest_year].max()) + '. Carbon in recovered products in use are recycled wood and paper that reenters the products in use category. Carbon emissions are displayed in units of carbon dioxide equivalent (CO2e) and do not include other carbon-based greenhouse gases such as methane.',
                        'total_recycled_carbon_co2e',
                        'Metric Tons CO2e')
                                                         
        # CUMULATIVE  PRESENT RECOVERED PRODUCTS CARBON MGC
        recycled_carbon_mgc = total_all_dispositions[[nm.Fields.harvest_year,nm.Fields.mgc(P(nm.Fields.recycled))]]
        self.generate_graph(recycled_carbon_mgc,
                        recycled_carbon_mgc[nm.Fields.mgc(P(nm.Fields.recycled))],
                        total_all_dispositions[nm.Fields.harvest_year],
                        0.3,
                        'Total Cumulative Carbon in Recovered Products in Use',
                        'Total cumulative megagrams carbon stored in recovered products in use manufactured from total timber harvested from ' + str(total_all_dispositions[nm.Fields.harvest_year].min()) + ' to ' + str(total_all_dispositions[nm.Fields.harvest_year].max()) + '. Carbon in recovered products in use are recycled wood and paper that reenters the products in use category.',
                        'total_recycled_carbon_mgc',
                        'Megagrams Carbon')
        
        self.generate_graph_no_caption(recycled_carbon_mgc,
                        recycled_carbon_mgc[nm.Fields.mgc(P(nm.Fields.recycled))],
                        total_all_dispositions[nm.Fields.harvest_year],
                        0.3,
                        'Total Cumulative Carbon in Recovered Products in Use',
                        'Total cumulative megagrams carbon stored in recovered products in use manufactured from total timber harvested from ' + str(total_all_dispositions[nm.Fields.harvest_year].min()) + ' to ' + str(total_all_dispositions[nm.Fields.harvest_year].max()) + '. Carbon in recovered products in use are recycled wood and paper that reenters the products in use category.',
                        'total_recycled_carbon_mgc',
                        'Megagrams Carbon')

        # CUMULATIVE RECOVERED PRODUCTS CO2E
        recycled_emit = total_all_dispositions[[nm.Fields.harvest_year,nm.Fields.co2(E(nm.Fields.recycled))]]
        self.generate_graph(recycled_emit,
                        recycled_emit[nm.Fields.co2(E(nm.Fields.recycled))],
                        total_all_dispositions[nm.Fields.harvest_year],
                        0.4,
                        'Total Cumulative Carbon Emitted from \n Recovered Products',
                        'Total cumulative metric tons carbon emitted from recovered products manufactured from total timber harvested from ' + str(total_all_dispositions[nm.Fields.harvest_year].min()) + ' to ' + str(total_all_dispositions[nm.Fields.harvest_year].max()) + '. Carbon emitted from recovered products in use is recycled wood and paper that reenters the products in use category. Carbon emissions are displayed in units of carbon dioxide equivalent (CO2e) and do not include other carbon-based greenhouse gases such as methane.',
                        'total_recycled_carbon_emitted',
                        'Metric Tons CO2e')
        
        self.generate_graph_no_caption(recycled_emit,
                        recycled_emit[nm.Fields.co2(E(nm.Fields.recycled))],
                        total_all_dispositions[nm.Fields.harvest_year],
                        0.4,
                        'Total Cumulative Carbon Emitted from \n Recovered Products',
                        'Total cumulative metric tons carbon emitted from recovered products manufactured from total timber harvested from ' + str(total_all_dispositions[nm.Fields.harvest_year].min()) + ' to ' + str(total_all_dispositions[nm.Fields.harvest_year].max()) + '. Carbon emitted from recovered products in use is recycled wood and paper that reenters the products in use category. Carbon emissions are displayed in units of carbon dioxide equivalent (CO2e) and do not include other carbon-based greenhouse gases such as methane.',
                        'total_recycled_carbon_emitted',
                        'Metric Tons CO2e')

        # CUMULATIVE EMIT FROM DISCARD PRODUCTS WITH ENERGY CAPTURE (FUEL)
        burned_w_energy_capture_emit = burned_w_energy_capture[nm.Fields.burned_with_energy_capture]
        self.generate_graph(burned_w_energy_capture_emit,
                        burned_w_energy_capture_emit,
                        burned_w_energy_capture_emit.index,
                        0.4,
                        'Total Cumulative Carbon Emitted from Burning Discard Products \n with Energy Capture',
                        'Total cumulative metric ton carbon emitted from burning discarded products with energy capture manufactured from total timber harvested from ' + str(burned_w_energy_capture_emit.index.min()) + ' to ' + str(burned_w_energy_capture_emit.index.max()) + '. Discarded products are assumed to be burned in an incinerator with energy capture. Emmitted carbon is displayed in units of carbon dioxide equivalent (CO2e) and do not include other carbon-based greenhouse gases such as methane.',
                        'burned_w_energy_capture_emitted',
                        'Metric Tons CO2e')
        
        self.generate_graph_no_caption(burned_w_energy_capture_emit,
                        burned_w_energy_capture_emit,
                        burned_w_energy_capture_emit.index,
                        0.4,
                        'Total Cumulative Carbon Emitted from Burning Discard Products \n with Energy Capture',
                        'Total cumulative metric ton carbon emitted from burning discarded products with energy capture manufactured from total timber harvested from ' + str(burned_w_energy_capture_emit.index.min()) + ' to ' + str(burned_w_energy_capture_emit.index.max()) + '. Discarded products are assumed to be burned in an incinerator with energy capture. Emmitted carbon is displayed in units of carbon dioxide equivalent (CO2e) and do not include other carbon-based greenhouse gases such as methane.',
                        'burned_w_energy_capture_emitted',
                        'Metric Tons CO2e')

        # CUMULATIVE EMIT FROM DISCARD PRODUCTS WITH ENERGY CAPTURE (FUEL)
        burned_wo_energy_capture_emit = burned_wo_energy_capture[nm.Fields.emitted]
        self.generate_graph(burned_wo_energy_capture_emit,
                        burned_wo_energy_capture_emit,
                        total_all_dispositions[nm.Fields.harvest_year],
                        0.4,
                        'Total Cumulative Carbon Emitted from Burning Discard Products \n without Energy Capture',
                        'Total cumulative metric tons carbon emitted from burning discarded products without energy capture manufactured from total timber harvested from ' + str(total_all_dispositions[nm.Fields.harvest_year].min()) + ' to ' + str(total_all_dispositions[nm.Fields.harvest_year].max()) + '. Carbon emiited from burned discarded products is assumed to be emitted without energy capture. Carbon emissions are displayed in units of carbon dioxide equivalent (CO2e) and do not include other carbon-based greenhouse gases such as methane.',
                        'burned_wo_energy_capture_emit',
                        'Metric Tons CO2e')

        self.generate_graph_no_caption(burned_wo_energy_capture_emit,
                        burned_wo_energy_capture_emit,
                        total_all_dispositions[nm.Fields.harvest_year],
                        0.4,
                        'Total Cumulative Carbon Emitted from Burning Discard Products \n without Energy Capture',
                        'Total cumulative metric tons carbon emitted from burning discarded products without energy capture manufactured from total timber harvested from ' + str(total_all_dispositions[nm.Fields.harvest_year].min()) + ' to ' + str(total_all_dispositions[nm.Fields.harvest_year].max()) + '. Carbon emiited from burned discarded products is assumed to be emitted without energy capture. Carbon emissions are displayed in units of carbon dioxide equivalent (CO2e) and do not include other carbon-based greenhouse gases such as methane.',
                        'burned_wo_energy_capture_emit',
                        'Metric Tons CO2e')

        # CUMULATIVE DISCARD COMPOST CO2E
        composted_emit = total_all_dispositions[[nm.Fields.harvest_year,nm.Fields.co2(E(nm.Fields.composted))]]
        self.generate_graph(composted_emit,
                        composted_emit[nm.Fields.co2(E(nm.Fields.composted))],
                        total_all_dispositions[nm.Fields.harvest_year],
                        0.5,
                        'Total Cumulative Carbon Emitted from Compost',
                        'Total cumulative metric tons carbon emitted from composted discarded harvested wood products manufactured from total timber harvested from ' + str(total_all_dispositions[nm.Fields.harvest_year].min()) + ' to ' + str(total_all_dispositions[nm.Fields.harvest_year].max()) + '. No carbon storage is associated with composted discarded products and all composted carbon is decay emitted without energy capture. Carbon emissions are displayed in units of carbon dioxide equivalent (CO2e) and do not include other greenhouse gases such as methane.',
                        'total_composted_carbon_emitted',
                        'Metric Tons CO2e')
        self.generate_graph_no_caption(composted_emit,
                        composted_emit[nm.Fields.co2(E(nm.Fields.composted))],
                        total_all_dispositions[nm.Fields.harvest_year],
                        0.5,
                        'Total Cumulative Carbon Emitted from Compost',
                        'Total cumulative metric tons carbon emitted from composted discarded harvested wood products manufactured from total timber harvested from ' + str(total_all_dispositions[nm.Fields.harvest_year].min()) + ' to ' + str(total_all_dispositions[nm.Fields.harvest_year].max()) + '. No carbon storage is associated with composted discarded products and all composted carbon is decay emitted without energy capture. Carbon emissions are displayed in units of carbon dioxide equivalent (CO2e) and do not include other greenhouse gases such as methane.',
                        'total_composted_carbon_emitted',
                        'Metric Tons CO2e')

        # CUMULATIVE DISCARD LANDFILL CARBON CO2E
        landfills_carbon = total_all_dispositions[[nm.Fields.harvest_year,nm.Fields.co2(P(nm.Fields.landfills))]]
        self.generate_graph(landfills_carbon,
                        landfills_carbon[nm.Fields.co2(P(nm.Fields.landfills))],
                        total_all_dispositions[nm.Fields.harvest_year],
                        0.35,
                        'Total Cumulative Carbon in Landfills',
                        'Total cumulative metric tons carbon stored in landfills from discarded products manufactured from total timber harvested from ' + str(total_all_dispositions[nm.Fields.harvest_year].min()) + ' to ' + str(total_all_dispositions[nm.Fields.harvest_year].max()) + '. Carbon in landfills are discarded wood and paper products and comprise a portion of the solid waste disposal site pool. Carbon emissions are displayed in units of carbon dioxide equivalent (CO2e) and do not include other carbon-based greenhouse gases such as methane.',
                        'total_landfills_carbon_co2e',
                        'Metric Tons CO2e')

        self.generate_graph_no_caption(landfills_carbon,
                        landfills_carbon[nm.Fields.co2(P(nm.Fields.landfills))],
                        total_all_dispositions[nm.Fields.harvest_year],
                        0.35,
                        'Total Cumulative Carbon in Landfills',
                        'Total cumulative metric tons carbon stored in landfills from discarded products manufactured from total timber harvested from ' + str(total_all_dispositions[nm.Fields.harvest_year].min()) + ' to ' + str(total_all_dispositions[nm.Fields.harvest_year].max()) + '. Carbon in landfills are discarded wood and paper products and comprise a portion of the solid waste disposal site pool. Carbon emissions are displayed in units of carbon dioxide equivalent (CO2e) and do not include other carbon-based greenhouse gases such as methane.',
                        'total_landfills_carbon_co2e',
                        'Metric Tons CO2e')

        # CUMULATIVE DISCARD LANDFILL CARBON MGC
        landfills_carbon_mgc = total_all_dispositions[[nm.Fields.harvest_year,nm.Fields.mgc(P(nm.Fields.landfills))]]
        self.generate_graph(landfills_carbon_mgc,
                        landfills_carbon_mgc[nm.Fields.mgc(P(nm.Fields.landfills))],
                        total_all_dispositions[nm.Fields.harvest_year],
                        0.35,
                        'Total Cumulative Carbon in Landfills',
                        'Total cumulative metric tons carbon stored in landfills from discarded products manufactured from total timber harvested from ' + str(total_all_dispositions[nm.Fields.harvest_year].min()) + ' to ' + str(total_all_dispositions[nm.Fields.harvest_year].max()) + '. Carbon in landfills are discarded wood and paper products and comprise a portion of the solid waste disposal site pool.',
                        'total_landfills_carbon_mgc',
                        'Megagrams Carbon')
        
        self.generate_graph_no_caption(landfills_carbon_mgc,
                        landfills_carbon_mgc[nm.Fields.mgc(P(nm.Fields.landfills))],
                        total_all_dispositions[nm.Fields.harvest_year],
                        0.35,
                        'Total Cumulative Carbon in Landfills',
                        'Total cumulative metric tons carbon stored in landfills from discarded products manufactured from total timber harvested from ' + str(total_all_dispositions[nm.Fields.harvest_year].min()) + ' to ' + str(total_all_dispositions[nm.Fields.harvest_year].max()) + '. Carbon in landfills are discarded wood and paper products and comprise a portion of the solid waste disposal site pool.',
                        'total_landfills_carbon_mgc',
                        'Megagrams Carbon')

        # CUMULATIVE DISCARD LANDFILL CO2E
        landfills_emit = total_all_dispositions[[nm.Fields.harvest_year,nm.Fields.co2(E(nm.Fields.landfills))]]
        self.generate_graph(landfills_emit,
                        landfills_emit[nm.Fields.co2(E(nm.Fields.landfills))],
                        total_all_dispositions[nm.Fields.harvest_year],
                        0.5,
                        'Total Cumulative Carbon Emitted from Landfills',
                        'Total cumulative metric tons carbon emitted from discarded produts in landfills manufactured from total timber harvested from ' + str(total_all_dispositions[nm.Fields.harvest_year].min()) + ' to ' + str(total_all_dispositions[nm.Fields.harvest_year].max()) + '. Carbon emitted from discarded wood and paper products in landfills is decay without energy capture. Methane remediation from landfills that includes combustion and subsequent emissions with energy capture is not included. Carbon emissions are displayed in usnits of carbon dioxide equivalent (CO2e) and do not include other carbon-based greenhouse gases such as methane.',
                        'total_landfills_carbon_emitted',
                        'Metric Tons CO2e')

        self.generate_graph_no_caption(landfills_emit,
                        landfills_emit[nm.Fields.co2(E(nm.Fields.landfills))],
                        total_all_dispositions[nm.Fields.harvest_year],
                        0.5,
                        'Total Cumulative Carbon Emitted from Landfills',
                        'Total cumulative metric tons carbon emitted from discarded produts in landfills manufactured from total timber harvested from ' + str(total_all_dispositions[nm.Fields.harvest_year].min()) + ' to ' + str(total_all_dispositions[nm.Fields.harvest_year].max()) + '. Carbon emitted from discarded wood and paper products in landfills is decay without energy capture. Methane remediation from landfills that includes combustion and subsequent emissions with energy capture is not included. Carbon emissions are displayed in usnits of carbon dioxide equivalent (CO2e) and do not include other carbon-based greenhouse gases such as methane.',
                        'total_landfills_carbon_emitted',
                        'Metric Tons CO2e')
        
        # CUMULATIVE DISCARD DUMPS CARBON CO2E
        dumps_carbon = total_all_dispositions[[nm.Fields.harvest_year,nm.Fields.co2(P(nm.Fields.dumps))]]
        self.generate_graph(dumps_carbon,
                        dumps_carbon[nm.Fields.co2(P(nm.Fields.dumps))],
                        total_all_dispositions[nm.Fields.harvest_year],
                        0.45,
                        'Total Cumulative Carbon in Dumps',
                        'Total cumulative metric tons carbon stored in dumps from discarded products manufactured from total timber harvested from ' + str(total_all_dispositions[nm.Fields.harvest_year].min()) + ' to ' + str(total_all_dispositions[nm.Fields.harvest_year].max()) + '. Carbon in dumps include discarded wood and paper products and comprise a portion of the solid waste disposal site pool. Prior to 1970, wood and paper waste was generally discarded to dumps, as opposed to modern landfills. Carbon emissions are displayed in units of carbon dioxide equivalent (CO2e) and do not include other carbon-based greenhouse gases such as methane.',
                        'total_dumps_carbon_co2e',
                        'Metric Tons CO2e')

        self.generate_graph_no_caption(dumps_carbon,
                        dumps_carbon[nm.Fields.co2(P(nm.Fields.dumps))],
                        total_all_dispositions[nm.Fields.harvest_year],
                        0.45,
                        'Total Cumulative Carbon in Dumps',
                        'Total cumulative metric tons carbon stored in dumps from discarded products manufactured from total timber harvested from ' + str(total_all_dispositions[nm.Fields.harvest_year].min()) + ' to ' + str(total_all_dispositions[nm.Fields.harvest_year].max()) + '. Carbon in dumps include discarded wood and paper products and comprise a portion of the solid waste disposal site pool. Prior to 1970, wood and paper waste was generally discarded to dumps, as opposed to modern landfills. Carbon emissions are displayed in units of carbon dioxide equivalent (CO2e) and do not include other carbon-based greenhouse gases such as methane.',
                        'total_dumps_carbon_co2e',
                        'Metric Tons CO2e')
        
        # CUMULATIVE DISCARD DUMPS CARBON MGC
        dumps_carbon_mgc = total_all_dispositions[[nm.Fields.harvest_year,nm.Fields.mgc(P(nm.Fields.dumps))]]
        self.generate_graph(dumps_carbon_mgc,
                        dumps_carbon_mgc[nm.Fields.mgc(P(nm.Fields.dumps))],
                        total_all_dispositions[nm.Fields.harvest_year],
                        0.45,
                        'Total Cumulative Carbon in Dumps',
                        'Total cumulative metric tons carbon stored in dumps from discarded products manufactured from total timber harvested from ' + str(total_all_dispositions[nm.Fields.harvest_year].min()) + ' to ' + str(total_all_dispositions[nm.Fields.harvest_year].max()) + '. Carbon in dumps include discarded wood and paper products and comprise a portion of the solid waste disposal site pool. Prior to 1970, wood and paper waste was generally discarded to dumps, as opposed to modern landfills.',
                        'total_dumps_carbon_mgc',
                        'Megagrams Carbon')
        
        self.generate_graph_no_caption(dumps_carbon_mgc,
                        dumps_carbon_mgc[nm.Fields.mgc(P(nm.Fields.dumps))],
                        total_all_dispositions[nm.Fields.harvest_year],
                        0.45,
                        'Total Cumulative Carbon in Dumps',
                        'Total cumulative metric tons carbon stored in dumps from discarded products manufactured from total timber harvested from ' + str(total_all_dispositions[nm.Fields.harvest_year].min()) + ' to ' + str(total_all_dispositions[nm.Fields.harvest_year].max()) + '. Carbon in dumps include discarded wood and paper products and comprise a portion of the solid waste disposal site pool. Prior to 1970, wood and paper waste was generally discarded to dumps, as opposed to modern landfills.',
                        'total_dumps_carbon_mgc',
                        'Megagrams Carbon')

        # CUMULATIVE DISCARD DUMPS CO2E
        dumps_emit = total_all_dispositions[[nm.Fields.harvest_year,nm.Fields.co2(E(nm.Fields.dumps))]]
        self.generate_graph(dumps_emit,
                        dumps_emit[nm.Fields.co2(E(nm.Fields.dumps))],
                        total_all_dispositions[nm.Fields.harvest_year],
                        0.5,
                        'Total Cumulative Carbon Emitted from Dumps',
                        'Total cumulative metric tons carbon emitted from discarded products in dumps manufactured from total timber harvested from ' + str(total_all_dispositions[nm.Fields.harvest_year].min()) + ' to ' + str(total_all_dispositions[nm.Fields.harvest_year].max()) + '. Carbon emitted from discarded wood and paper products in dumps is decay without energy capture. Prior to 1970 wood and paper waste was generally discarded to dumps, where it was subject to higher rates of decay than in modern landfills. Carbon emissions are displayed in units of carbon dioxide equivalent (CO2e) and do not include other carbon-based greenhouse gases such as methane.',
                        'total_dumps_carbon_emitted',
                        'Metric Tons CO2e')

        self.generate_graph_no_caption(dumps_emit,
                        dumps_emit[nm.Fields.co2(E(nm.Fields.dumps))],
                        total_all_dispositions[nm.Fields.harvest_year],
                        0.5,
                        'Total Cumulative Carbon Emitted from Dumps',
                        'Total cumulative metric tons carbon emitted from discarded products in dumps manufactured from total timber harvested from ' + str(total_all_dispositions[nm.Fields.harvest_year].min()) + ' to ' + str(total_all_dispositions[nm.Fields.harvest_year].max()) + '. Carbon emitted from discarded wood and paper products in dumps is decay without energy capture. Prior to 1970 wood and paper waste was generally discarded to dumps, where it was subject to higher rates of decay than in modern landfills. Carbon emissions are displayed in units of carbon dioxide equivalent (CO2e) and do not include other carbon-based greenhouse gases such as methane.',
                        'total_dumps_carbon_emitted',
                        'Metric Tons CO2e')
        
        fuelwood_emit = total_all_dispositions[[nm.Fields.harvest_year,nm.Fields.co2(E(nm.Fields.fuel))]]
        self.generate_graph(fuelwood_emit,
                        fuelwood_emit[nm.Fields.co2(E(nm.Fields.fuel))],
                        total_all_dispositions[nm.Fields.harvest_year],
                        0.5,
                        'Total Cumulative Carbon Emitted from Fuelwood with Energy Capture',
                        'Total cumulative metric tons carbon emitted from fuelwood and wood waste used for fuel with energy capture from total timber harvested from ' + str(total_all_dispositions[nm.Fields.harvest_year].min()) + ' to ' + str(total_all_dispositions[nm.Fields.harvest_year].max()) + '. Carbon emitted from burning fuelwood and wood waste with energy capture occurs during the year of harvest and is not assumed to substitute for an equivalent amount of fossil fuel carbon. Carbon emissions are displayed in units of carbon dioxide equivalent (CO2e) and do not include other carbon-based greenhouse gases such as methane.',
                        'total_fuelwood_carbon_emitted',
                        'Metric Tons CO2e')

        self.generate_graph_no_caption(fuelwood_emit,
                        fuelwood_emit[nm.Fields.co2(E(nm.Fields.fuel))],
                        total_all_dispositions[nm.Fields.harvest_year],
                        0.5,
                        'Total Cumulative Carbon Emitted from Fuelwood with Energy Capture',
                        'Total cumulative metric tons carbon emitted from fuelwood and wood waste used for fuel with energy capture from total timber harvested from ' + str(total_all_dispositions[nm.Fields.harvest_year].min()) + ' to ' + str(total_all_dispositions[nm.Fields.harvest_year].max()) + '. Carbon emitted from burning fuelwood and wood waste with energy capture occurs during the year of harvest and is not assumed to substitute for an equivalent amount of fossil fuel carbon. Carbon emissions are displayed in units of carbon dioxide equivalent (CO2e) and do not include other carbon-based greenhouse gases such as methane.',
                        'total_fuelwood_carbon_emitted',
                        'Metric Tons CO2e')

        # ALL DISPOSITIONS
        with tempfile.TemporaryFile() as temp:
            total_all_dispositions.to_csv(temp)
            temp.seek(0)
            self.zip.writestr('all_dispositions.csv', temp.read(), compress_type=zipfile.ZIP_STORED)

        # PRIMARY PRODUCTS
        with tempfile.TemporaryFile() as temp:
            primary_products.to_csv(temp)
            temp.seek(0)
            self.zip.writestr('primary_products.csv', temp.read(), compress_type=zipfile.ZIP_STORED)

        # CARBON STOCKS
        with tempfile.TemporaryFile() as temp:
            total_in_use.to_csv(temp)
            temp.seek(0)
            self.zip.writestr('total_in_use.csv', temp.read(), compress_type=zipfile.ZIP_STORED)

        
        self.generate_carbon_stocks_graph(big_table,"co2e")
        self.generate_carbon_stocks_graph(big_table,"mgc")
        self.generate_carbon_stocks_graph_no_caption(big_table,"co2e")
        self.generate_carbon_stocks_graph_no_caption(big_table,"mgc")

        self.generate_carbon_stocks_change_graph("co2e")
        self.generate_carbon_stocks_change_graph("mgc")
        self.generate_carbon_stocks_change_graph_no_caption("co2e")
        self.generate_carbon_stocks_change_graph_no_caption("mgc")

        self.generate_annual_harvest_and_timber_product_graph(annual_timber_products)

        self.generate_big_table_graph(big_table,"co2e")
        self.generate_big_table_graph(big_table,"mgc")

#--------------------------------------------------------

        with tempfile.TemporaryFile() as temp:
            captions_json = json.dumps(self.captions)
            captions_json = captions_json.encode()
            temp.write(captions_json)
            temp.seek(0)
            self.zip.writestr('captions.json', temp.read(), compress_type=zipfile.ZIP_STORED)
        
        
        if not os.path.exists('./output/'):
            os.makedirs('./output')
        
        self.zip.close()
        self.zip_buffer.seek(0)

        print('Output Path:', nm.Output.output_path)
        print('Run Name:', nm.Output.run_name)
        
        gch.upload_temp('hwpcarbon-data', self.zip_buffer, nm.Output.output_path + '/results/' + nm.Output.run_name + '.zip', 'application/zip')
        # with open('./output/results.zip', 'wb') as f:
        #     f.write(self.zip_buffer.getvalue())

        self.zip_buffer.close()

        # with open('results/results.json', 'w') as outfile:
        #     json.dump(results_json, outfile)

        # gch.upload_blob('hwpcarbon-data','results/results.json', nm.Output.output_path + '/results/results.json')
        
        return
    
    def save_fuel_captured(self):
        # print(self.fuel_captured.axes)
        # fc = pd.DataFrame(self.fuel_captured)
        # fc_total_fuel_captured = fc.groupby(by='Year')['burned_captured'].sum()
        # plt.xlabel('Years')
        # plt.ylabel('Burned Captured (ccf)')
        # plt.plot(fc_total_fuel_captured)
        # plt.show()
        # self.fuel_captured = self.fuel_captured.cumsum(Index='burn_caputured')
        # fc_total_fuel_captured.to_csv('fuel_captured.csv')
        return
    
    def save_end_use_products(self):
        # self.end_use_products_step.to_csv('end_use_products.csv')
        return
    
    def save_discarded_wood_or_paper(self):
        dwp = pd.DataFrame(self.discarded_wood_paper)
        dwp = dwp.groupby(by='Year')[nm.Fields.discard_wood_paper].sum()
        dwp.to_csv("results/discarded_wood_or_paper.csv")
        plt.subplots_adjust(bottom=0.45)
        plt.title('Total Cumulative Carbon Emitted from Dumps')
        plt.xlabel('Inventory Year')
        plt.ylabel('Metric Tons C')
        plt.plot(dwp)
        plt.ticklabel_format(axis='y',style='sci',scilimits=(1,5))
        plt.savefig('results/total_discarded_wood_or_paper')
        return 

    def total_yearly_harvest(self):

        df = pd.DataFrame(self.primary_products)
        print(self.md.data[nm.Tables.primary_products])
        df = df.merge(self.md.data[nm.Tables.primary_products], how='outer', on=[nm.Fields.timber_product_id, nm.Fields.primary_product_id])
        n = nm.Fields.co2(nm.Fields.timber_product_results)
        print(df)
        # df[n] = df[nm.Fields.timber_product_results] * df[nm.Fields.conversion_factor]
        # df_sum = df.groupby(by=nm.Fields.harvest_year)[n].mode()


        return

    def generate_graph(self,df_for_csv,data_frame,xaxis,adjust_bottom,title,txt,file_name,y_axis):

        try:
            with tempfile.TemporaryFile() as temp:
                df_for_csv.to_csv(temp)
                temp.seek(0)
                self.zip.writestr(file_name+'.csv', temp.read(), compress_type=zipfile.ZIP_STORED)
            fig, ax = plt.subplots()
            plt.subplots_adjust(bottom = adjust_bottom)
            plt.title(title, multialignment='center')
            plt.xlabel('Inventory Year')
            
            if(title=="Total Cumulative Carbon Emitted from Burning Discard Products \n with Energy Capture"):
                plt.ylim(-1,1) 
            ax.plot(xaxis,data_frame)
            plt.ticklabel_format(axis='y',style='sci',scilimits=(1,5))
            plt.figtext(0.5, 0.05, txt, wrap=True, horizontalalignment='center', fontsize=12)
            Labeloffset(ax, label=y_axis, axis="y")
            plt.rcParams["figure.figsize"] = (8,6)
            with tempfile.TemporaryFile(suffix=".png") as temp:
                plt.savefig(temp, format="png", pad_inches=0.1) # File position is at the end of the file.
                temp.seek(0) # Rewind the file. (0: the beginning of the file)
                self.zip.writestr(file_name+'.png', temp.read(), compress_type=zipfile.ZIP_STORED)
            plt.clf()
            plt.close()

        except:
            print("Graph could not generate")
           


        return

    def generate_graph_no_caption(self,df_for_csv,data_frame,xaxis,adjust_bottom,title,txt,file_name,y_axis):

        try:
            self.captions[file_name+'_caption'] = txt
            fig, ax = plt.subplots()
            plt.title(title, multialignment='center')
            plt.xlabel('Inventory Year')
            if(title=="Total Cumulative Carbon Emitted from Burning Discard Products \n with Energy Capture"):
                plt.ylim(-1,1) 
            ax.plot(xaxis,data_frame)
            plt.ticklabel_format(axis='y',style='sci',scilimits=(1,5))
            Labeloffset(ax, label=y_axis, axis="y")
            plt.rcParams["figure.figsize"] = (8,6)
            with tempfile.TemporaryFile(suffix=".png") as temp:
                plt.savefig(temp, format="png", pad_inches=0.1) # File position is at the end of the file.
                temp.seek(0) # Rewind the file. (0: the beginning of the file)
                self.zip.writestr(file_name+'_no_caption.png', temp.read(), compress_type=zipfile.ZIP_STORED)
            plt.clf()
            plt.close()

        except:
            print("Graph could not generate")
           


        return

    def generate_carbon_stocks_graph(self,big_table,units):
        P = nm.Fields.ppresent
        if(units == "co2e"):
            products_in_use = self.big_table[[nm.Fields.harvest_year,nm.Fields.co2(nm.Fields.products_in_use)]]
            with tempfile.TemporaryFile() as temp:
                products_in_use.to_csv(temp)
                temp.seek(0)
                self.zip.writestr('products_in_use_co2e.csv', temp.read(), compress_type=zipfile.ZIP_STORED)

            swds = self.big_table[[nm.Fields.harvest_year,nm.Fields.co2(P(nm.Fields.swds))]]
            with tempfile.TemporaryFile() as temp:
                swds.to_csv(temp)
                temp.seek(0)
                self.zip.writestr('swds_co2e.csv', temp.read(), compress_type=zipfile.ZIP_STORED)
            
            fig, ax = plt.subplots()
            plt.subplots_adjust(bottom=0.25)
            plt.title('Total Cumulative Carbon Stocks')
            color = 'tab:red'
            plt.xlabel('Inventory Year')
            plt.ticklabel_format(axis='y',style='sci',scilimits=(1,5))
            txt = 'Total cumulative metric tons of carbon stocks in harvested wood products (HWP) manufactured from total timber harvested from ' + str(big_table[nm.Fields.harvest_year].min()) + ' to ' + str(big_table[nm.Fields.harvest_year].max()) + ' using the IPCC Tier 3 Production Approach. \n Carbon in HWP includes both products that are still in use and carbon stored at solid waste disposal sites (SWDS). \n Carbon emissions are displayed in units of carbon dioxide equivalent (CO2e) and do not include other carbon-based greenhouse gases such as methane.'
            plt.figtext(0.5, 0.05, txt, wrap=True, horizontalalignment='center', fontsize=12)
            ax.stackplot(big_table[nm.Fields.harvest_year],big_table[nm.Fields.co2(nm.Fields.products_in_use)].values,big_table[nm.Fields.co2(P(nm.Fields.swds))].values, colors=("tab:red","tab:blue"),labels=("Products In Use", "SWDS"))
            Labeloffset(ax, label="Total Carbon Stocks Metric Tons CO2e", axis="y")
            ax.legend()
            plt.rcParams["figure.figsize"] = (8,6)
            with tempfile.TemporaryFile(suffix=".png") as temp:
                plt.savefig(temp, format="png", pad_inches=0.1, bbox_inches = "tight") # File position is at the end of the file.
                temp.seek(0) # Rewind the file. (0: the beginning of the file)
                self.zip.writestr('total_cumulative_carbon_stocks_co2e.png', temp.read(), compress_type=zipfile.ZIP_STORED)
            plt.clf()
            plt.close()
        else:
            products_in_use = self.big_table[[nm.Fields.harvest_year,nm.Fields.mgc(nm.Fields.products_in_use)]]
            with tempfile.TemporaryFile() as temp:
                products_in_use.to_csv(temp)
                temp.seek(0)
                self.zip.writestr('products_in_use_mgc.csv', temp.read(), compress_type=zipfile.ZIP_STORED)

            swds = self.big_table[[nm.Fields.harvest_year,nm.Fields.mgc(P(nm.Fields.swds))]]
            with tempfile.TemporaryFile() as temp:
                swds.to_csv(temp)
                temp.seek(0)
                self.zip.writestr('swds_mgc.csv', temp.read(), compress_type=zipfile.ZIP_STORED)
            
            fig, ax = plt.subplots()
            plt.subplots_adjust(bottom=0.25)
            plt.title('Total Cumulative Carbon Stocks')
            color = 'tab:red'
            plt.xlabel('Inventory Year')
            plt.ticklabel_format(axis='y',style='sci',scilimits=(1,5))
            txt = 'Total cumulative metric tons of carbon stocks in harvested wood products (HWP) manufactured from total timber harvested from ' + str(big_table[nm.Fields.harvest_year].min()) + ' to ' + str(big_table[nm.Fields.harvest_year].max()) + ' using the IPCC Tier 3 Production Approach. \n Carbon in HWP includes both products that are still in use and carbon stored at solid waste disposal sites (SWDS).'
            plt.figtext(0.5, 0.05, txt, wrap=True, horizontalalignment='center', fontsize=12)
            ax.stackplot(big_table[nm.Fields.harvest_year],big_table[nm.Fields.mgc(nm.Fields.products_in_use)].values,big_table[nm.Fields.mgc(P(nm.Fields.swds))].values, colors=("tab:red","tab:blue"),labels=("Products In Use", "SWDS"))
            Labeloffset(ax, label="Total Carbon Stocks Megagrams Carbon", axis="y")
            ax.legend()
            plt.rcParams["figure.figsize"] = (8,6)
            with tempfile.TemporaryFile(suffix=".png") as temp:
                plt.savefig(temp, format="png", pad_inches=0.1, bbox_inches = "tight") # File position is at the end of the file.
                temp.seek(0) # Rewind the file. (0: the beginning of the file)
                self.zip.writestr('total_cumulative_carbon_stocks_mgc.png', temp.read(), compress_type=zipfile.ZIP_STORED)
            plt.clf()
            plt.close()
        return

    def generate_carbon_stocks_graph_no_caption(self,big_table,units):
        P = nm.Fields.ppresent
        if(units == "co2e"):
            products_in_use = self.big_table[[nm.Fields.harvest_year,nm.Fields.co2(nm.Fields.products_in_use)]]
            # with tempfile.TemporaryFile() as temp:
            #     products_in_use.to_csv(temp)
            #     temp.seek(0)
            #     self.zip.writestr('products_in_use_co2e.csv', temp.read(), compress_type=zipfile.ZIP_STORED)

            swds = self.big_table[[nm.Fields.harvest_year,nm.Fields.co2(P(nm.Fields.swds))]]
            # with tempfile.TemporaryFile() as temp:
            #     swds.to_csv(temp)
            #     temp.seek(0)
            #     self.zip.writestr('swds_co2e.csv', temp.read(), compress_type=zipfile.ZIP_STORED)
            
            fig, ax = plt.subplots()
            #plt.subplots_adjust(bottom=0.25)
            plt.title('Total Cumulative Carbon Stocks')
            color = 'tab:red'
            plt.xlabel('Inventory Year')
            plt.ticklabel_format(axis='y',style='sci',scilimits=(1,5))
            txt = 'Total cumulative metric tons of carbon stocks in harvested wood products (HWP) manufactured from total timber harvested from ' + str(big_table[nm.Fields.harvest_year].min()) + ' to ' + str(big_table[nm.Fields.harvest_year].max()) + ' using the IPCC Tier 3 Production Approach. Carbon in HWP includes both products that are still in use and carbon stored at solid waste disposal sites (SWDS). Carbon emissions are displayed in units of carbon dioxide equivalent (CO2e) and do not include other carbon-based greenhouse gases such as methane.'
            self.captions['total_cumulative_carbon_stocks_co2e_caption'] = txt
            #plt.figtext(0.5, 0.05, txt, wrap=True, horizontalalignment='center', fontsize=12)
            ax.stackplot(big_table[nm.Fields.harvest_year],big_table[nm.Fields.co2(nm.Fields.products_in_use)].values,big_table[nm.Fields.co2(P(nm.Fields.swds))].values, colors=("tab:red","tab:blue"),labels=("Products In Use", "SWDS"))
            Labeloffset(ax, label="Total Carbon Stocks Metric Tons CO2e", axis="y")
            ax.legend()
            plt.rcParams["figure.figsize"] = (8,6)
            with tempfile.TemporaryFile(suffix=".png") as temp:
                plt.savefig(temp, format="png", pad_inches=0.1, bbox_inches = "tight") # File position is at the end of the file.
                temp.seek(0) # Rewind the file. (0: the beginning of the file)
                self.zip.writestr('total_cumulative_carbon_stocks_co2e_no_caption.png', temp.read(), compress_type=zipfile.ZIP_STORED)
            plt.clf()
            plt.close()
        else:
            products_in_use = self.big_table[[nm.Fields.harvest_year,nm.Fields.mgc(nm.Fields.products_in_use)]]
            # with tempfile.TemporaryFile() as temp:
            #     products_in_use.to_csv(temp)
            #     temp.seek(0)
            #     self.zip.writestr('products_in_use_mgc.csv', temp.read(), compress_type=zipfile.ZIP_STORED)

            swds = self.big_table[[nm.Fields.harvest_year,nm.Fields.mgc(P(nm.Fields.swds))]]
            # with tempfile.TemporaryFile() as temp:
            #     swds.to_csv(temp)
            #     temp.seek(0)
            #     self.zip.writestr('swds_mgc.csv', temp.read(), compress_type=zipfile.ZIP_STORED)
            
            fig, ax = plt.subplots()
            #plt.subplots_adjust(bottom=0.25)
            plt.title('Total Cumulative Carbon Stocks')
            color = 'tab:red'
            plt.xlabel('Inventory Year')
            plt.ticklabel_format(axis='y',style='sci',scilimits=(1,5))
            txt = 'Total cumulative metric tons of carbon stocks in harvested wood products (HWP) manufactured from total timber harvested from ' + str(big_table[nm.Fields.harvest_year].min()) + ' to ' + str(big_table[nm.Fields.harvest_year].max()) + ' using the IPCC Tier 3 Production Approach. Carbon in HWP includes both products that are still in use and carbon stored at solid waste disposal sites (SWDS).'
            self.captions['total_cumulative_carbon_stocks_mgc_caption'] = txt
            # plt.figtext(0.5, 0.05, txt, wrap=True, horizontalalignment='center', fontsize=12)
            ax.stackplot(big_table[nm.Fields.harvest_year],big_table[nm.Fields.mgc(nm.Fields.products_in_use)].values,big_table[nm.Fields.mgc(P(nm.Fields.swds))].values, colors=("tab:red","tab:blue"),labels=("Products In Use", "SWDS"))
            Labeloffset(ax, label="Total Carbon Stocks Megagrams Carbon", axis="y")
            ax.legend()
            plt.rcParams["figure.figsize"] = (8,6)
            with tempfile.TemporaryFile(suffix=".png") as temp:
                plt.savefig(temp, format="png", pad_inches=0.1, bbox_inches = "tight") # File position is at the end of the file.
                temp.seek(0) # Rewind the file. (0: the beginning of the file)
                self.zip.writestr('total_cumulative_carbon_stocks_mgc_no_caption.png', temp.read(), compress_type=zipfile.ZIP_STORED)
            plt.clf()
            plt.close()
        return

    def generate_carbon_stocks_change_graph(self,units):
        #CARBON CHANGE
        P = nm.Fields.ppresent
        final = pd.DataFrame(self.final)
        if(units == "co2e"):
            with tempfile.TemporaryFile() as temp:
                final.to_csv(temp)
                temp.seek(0)
                self.zip.writestr('final.csv', temp.read(), compress_type=zipfile.ZIP_STORED)
            #We sum products_in_use and swds_change to convert NaN values to 0, even if there is only one per year.
            products_in_use_change = final.groupby(by='Year')[nm.Fields.co2(nm.Fields.products_in_use)+"_change"].sum()
            swds_change = final.groupby(by='Year')[nm.Fields.co2(P(nm.Fields.swds))+"_change"].sum()
            
            fig, ax = plt.subplots()
            plt.subplots_adjust(bottom=0.25)
            plt.title('Annual Net Change in Carbon Stocks')
            color = 'tab:red'
            plt.xlabel('Inventory Year')
            plt.ticklabel_format(axis='y',style='sci',scilimits=(0,0))
            ax.axhline(0, color='grey', linewidth=0.8)
            txt = 'Total cumulative metric tons of carbon stocks in harvested wood products (HWP) manufactured from total timber harvested from ' + str(final[nm.Fields.harvest_year].min()) + ' to ' + str(final[nm.Fields.harvest_year].max()) + ' using the IPCC Tier 3 Production Approach. \n Carbon in HWP includes both products that are still in use and carbon stored at solid waste disposal sites (SWDS).\n Carbon emissions are displayed in units of carbon dioxide equivalent (CO2e) and do not include other carbon-based greenhouse gases such as methane.'
            plt.figtext(0.5, 0.05, txt, wrap=True, horizontalalignment='center', fontsize=12)
            p1 = ax.bar(final[nm.Fields.harvest_year],products_in_use_change,label="Products In Use",color=color)
            color = 'tab:blue'
            p2 = ax.bar(final[nm.Fields.harvest_year],swds_change, color=color, label="SWDS")
            Labeloffset(ax, label="Metric Tons CO2e", axis="y")
            ax.legend()
            plt.rcParams["figure.figsize"] = (8,6)
            with tempfile.TemporaryFile(suffix=".png") as temp:
                plt.savefig(temp, format="png", pad_inches=0.1, bbox_inches = "tight") # File position is at the end of the file.
                temp.seek(0) # Rewind the file. (0: the beginning of the file)
                self.zip.writestr('annual_net_change_carbon_stocks_co2e.png', temp.read(), compress_type=zipfile.ZIP_STORED)
            plt.clf()
            plt.close()
        else:
            #We sum products_in_use and swds_change to convert NaN values to 0, even if there is only one per year.
            products_in_use_change = final.groupby(by='Year')[nm.Fields.mgc(nm.Fields.products_in_use)+"_change"].sum()
            swds_change = final.groupby(by='Year')[nm.Fields.mgc(P(nm.Fields.swds))+"_change"].sum()
            
            fig, ax = plt.subplots()
            plt.subplots_adjust(bottom=0.25)
            plt.title('Annual Net Change in Carbon Stocks')
            color = 'tab:red'
            plt.xlabel('Inventory Year')
            plt.ticklabel_format(axis='y',style='sci',scilimits=(0,0))
            ax.axhline(0, color='grey', linewidth=0.8)
            txt = 'Total cumulative metric tons of carbon stocks in harvested wood products (HWP) manufactured from total timber harvested from ' + str(final[nm.Fields.harvest_year].min()) + ' to ' + str(final[nm.Fields.harvest_year].max()) + ' using the IPCC Tier 3 Production Approach. \n Carbon in HWP includes both products that are still in use and carbon stored at solid waste disposal sites (SWDS).\n Carbon emissions are displayed in units of carbon dioxide equivalent (CO2e) and do not include other carbon-based greenhouse gases such as methane.'
            plt.figtext(0.5, 0.05, txt, wrap=True, horizontalalignment='center', fontsize=12)
            p1 = ax.bar(final[nm.Fields.harvest_year],products_in_use_change,label="Products In Use",color=color)
            color = 'tab:blue'
            p2 = ax.bar(final[nm.Fields.harvest_year],swds_change, color=color, label="SWDS")
            Labeloffset(ax, label="Megagrams Carbon", axis="y")
            ax.legend()
            plt.rcParams["figure.figsize"] = (8,6)
            with tempfile.TemporaryFile(suffix=".png") as temp:
                plt.savefig(temp, format="png", pad_inches=0.1, bbox_inches = "tight") # File position is at the end of the file.
                temp.seek(0) # Rewind the file. (0: the beginning of the file)
                self.zip.writestr('annual_net_change_carbon_stocks_mgc.png', temp.read(), compress_type=zipfile.ZIP_STORED)
            plt.clf()
            plt.close()
        return
    
    def generate_carbon_stocks_change_graph_no_caption(self,units):
        #CARBON CHANGE
        P = nm.Fields.ppresent
        final = pd.DataFrame(self.final)
        if(units == "co2e"):
            # with tempfile.TemporaryFile() as temp:
            #     final.to_csv(temp)
            #     temp.seek(0)
            #     self.zip.writestr('final.csv', temp.read(), compress_type=zipfile.ZIP_STORED)
            #We sum products_in_use and swds_change to convert NaN values to 0, even if there is only one per year.
            products_in_use_change = final.groupby(by='Year')[nm.Fields.co2(nm.Fields.products_in_use)+"_change"].sum()
            swds_change = final.groupby(by='Year')[nm.Fields.co2(P(nm.Fields.swds))+"_change"].sum()
            
            fig, ax = plt.subplots()
            #plt.subplots_adjust(bottom=0.25)
            plt.title('Annual Net Change in Carbon Stocks')
            color = 'tab:red'
            plt.xlabel('Inventory Year')
            plt.ticklabel_format(axis='y',style='sci',scilimits=(0,0))
            ax.axhline(0, color='grey', linewidth=0.8)
            txt = 'Total cumulative metric tons of carbon stocks in harvested wood products (HWP) manufactured from total timber harvested from ' + str(final[nm.Fields.harvest_year].min()) + ' to ' + str(final[nm.Fields.harvest_year].max()) + ' using the IPCC Tier 3 Production Approach. Carbon in HWP includes both products that are still in use and carbon stored at solid waste disposal sites (SWDS). Carbon emissions are displayed in units of carbon dioxide equivalent (CO2e) and do not include other carbon-based greenhouse gases such as methane.'
            self.captions['annual_net_change_carbon_stocks_co2e_caption'] = txt
            #plt.figtext(0.5, 0.05, txt, wrap=True, horizontalalignment='center', fontsize=12)
            p1 = ax.bar(final[nm.Fields.harvest_year],products_in_use_change,label="Products In Use",color=color)
            color = 'tab:blue'
            p2 = ax.bar(final[nm.Fields.harvest_year],swds_change, color=color, label="SWDS")
            Labeloffset(ax, label="Metric Tons CO2e", axis="y")
            ax.legend()
            plt.rcParams["figure.figsize"] = (8,6)
            with tempfile.TemporaryFile(suffix=".png") as temp:
                plt.savefig(temp, format="png", pad_inches=0.1, bbox_inches = "tight") # File position is at the end of the file.
                temp.seek(0) # Rewind the file. (0: the beginning of the file)
                self.zip.writestr('annual_net_change_carbon_stocks_co2e_no_caption.png', temp.read(), compress_type=zipfile.ZIP_STORED)
            plt.clf()
            plt.close()
        else:
            #We sum products_in_use and swds_change to convert NaN values to 0, even if there is only one per year.
            products_in_use_change = final.groupby(by='Year')[nm.Fields.mgc(nm.Fields.products_in_use)+"_change"].sum()
            swds_change = final.groupby(by='Year')[nm.Fields.mgc(P(nm.Fields.swds))+"_change"].sum()
            
            fig, ax = plt.subplots()
            #plt.subplots_adjust(bottom=0.25)
            plt.title('Annual Net Change in Carbon Stocks')
            color = 'tab:red'
            plt.xlabel('Inventory Year')
            plt.ticklabel_format(axis='y',style='sci',scilimits=(0,0))
            ax.axhline(0, color='grey', linewidth=0.8)
            txt = 'Total cumulative metric tons of carbon stocks in harvested wood products (HWP) manufactured from total timber harvested from ' + str(final[nm.Fields.harvest_year].min()) + ' to ' + str(final[nm.Fields.harvest_year].max()) + ' using the IPCC Tier 3 Production Approach. Carbon in HWP includes both products that are still in use and carbon stored at solid waste disposal sites (SWDS). Carbon emissions are displayed in units of carbon dioxide equivalent (CO2e) and do not include other carbon-based greenhouse gases such as methane.'
            self.captions['annual_net_change_carbon_stocks_mgc_caption'] = txt
            #plt.figtext(0.5, 0.05, txt, wrap=True, horizontalalignment='center', fontsize=12)
            p1 = ax.bar(final[nm.Fields.harvest_year],products_in_use_change,label="Products In Use",color=color)
            color = 'tab:blue'
            p2 = ax.bar(final[nm.Fields.harvest_year],swds_change, color=color, label="SWDS")
            Labeloffset(ax, label="Megagrams Carbon", axis="y")
            ax.legend()
            plt.rcParams["figure.figsize"] = (8,6)
            with tempfile.TemporaryFile(suffix=".png") as temp:
                plt.savefig(temp, format="png", pad_inches=0.1, bbox_inches = "tight") # File position is at the end of the file.
                temp.seek(0) # Rewind the file. (0: the beginning of the file)
                self.zip.writestr('annual_net_change_carbon_stocks_mgc_no_caption.png', temp.read(), compress_type=zipfile.ZIP_STORED)
            plt.clf()
            plt.close()
        return

    def generate_annual_harvest_and_timber_product_graph(self,annual_timber_products):
        # TOTAL HARVEST AND TIMBER RESULTS
        timber_products_results = annual_timber_products[[nm.Fields.harvest_year, nm.Fields.primary_product_results]]
        with tempfile.TemporaryFile() as temp:
            timber_products_results.to_csv(temp)
            temp.seek(0)
            self.zip.writestr('annual_timber_product_output.csv', temp.read(), compress_type=zipfile.ZIP_STORED)
    
        harvests_results = annual_timber_products[[nm.Fields.harvest_year,nm.Fields.ccf]]
        with tempfile.TemporaryFile() as temp:
            harvests_results.to_csv(temp)
            temp.seek(0)
            self.zip.writestr('annual_harvests_output.csv', temp.read(), compress_type=zipfile.ZIP_STORED)
        
        color = 'tab:red'
        fig, ax = plt.subplots()
        plt.subplots_adjust(bottom=0.4)
        plt.title('Annual Harvest and Timber Product Output')
        plt.xlabel('Inventory Year')
        txt = 'Annual total timber harvest and product output converted to metric tons of carbon, from ' + str(timber_products_results[nm.Fields.harvest_year].min()) + ' to ' + str(timber_products_results[nm.Fields.harvest_year].max())
        plt.figtext(0.5, 0.05, txt, wrap=True, horizontalalignment='center', fontsize=12)
        ax.plot(timber_products_results[nm.Fields.harvest_year],timber_products_results[nm.Fields.primary_product_results], color=color,label="Timber Product Output (Metric Tons C)")
        color = 'tab:blue'
        ax.plot(timber_products_results[nm.Fields.harvest_year],harvests_results[nm.Fields.ccf], color=color,label="Annual Harvest (CCF)")
        Labeloffset(ax, label="Metric Tons Carbon", axis="y")
        ax.legend()
        plt.rcParams["figure.figsize"] = (8,6)
        with tempfile.TemporaryFile(suffix=".png") as temp:
            plt.savefig(temp, format="png", pad_inches=0.1, bbox_inches = "tight") # File position is at the end of the file.
            temp.seek(0) # Rewind the file. (0: the beginning of the file)
            self.zip.writestr('annual_harvest_and_timber_product_output.png', temp.read(), compress_type=zipfile.ZIP_STORED)
        plt.clf()
        plt.close()
        return

    def generate_annual_harvest_and_timber_product_graph_no_caption(self,annual_timber_products):
        # TOTAL HARVEST AND TIMBER RESULTS
        timber_products_results = annual_timber_products[[nm.Fields.harvest_year, nm.Fields.primary_product_results]]
        # with tempfile.TemporaryFile() as temp:
        #     timber_products_results.to_csv(temp)
        #     temp.seek(0)
        #     self.zip.writestr('annual_timber_product_output.csv', temp.read(), compress_type=zipfile.ZIP_STORED)
    
        harvests_results = annual_timber_products[[nm.Fields.harvest_year,nm.Fields.ccf]]
        # with tempfile.TemporaryFile() as temp:
        #     harvests_results.to_csv(temp)
        #     temp.seek(0)
        #     self.zip.writestr('annual_harvests_output.csv', temp.read(), compress_type=zipfile.ZIP_STORED)
        
        color = 'tab:red'
        fig, ax = plt.subplots()
        # plt.subplots_adjust(bottom=0.4)
        plt.title('Annual Harvest and Timber Product Output')
        plt.xlabel('Inventory Year')
        txt = 'Annual total timber harvest and product output converted to metric tons of carbon, from ' + str(timber_products_results[nm.Fields.harvest_year].min()) + ' to ' + str(timber_products_results[nm.Fields.harvest_year].max())
        self.captions['annual_harvest_and_timber_product_output_caption'] = txt
        #plt.figtext(0.5, 0.05, txt, wrap=True, horizontalalignment='center', fontsize=12)
        ax.plot(timber_products_results[nm.Fields.harvest_year],timber_products_results[nm.Fields.primary_product_results], color=color,label="Timber Product Output (Metric Tons C)")
        color = 'tab:blue'
        ax.plot(timber_products_results[nm.Fields.harvest_year],harvests_results[nm.Fields.ccf], color=color,label="Annual Harvest (CCF)")
        Labeloffset(ax, label="Metric Tons Carbon", axis="y")
        ax.legend()
        plt.rcParams["figure.figsize"] = (8,6)
        with tempfile.TemporaryFile(suffix=".png") as temp:
            plt.savefig(temp, format="png", pad_inches=0.1, bbox_inches = "tight") # File position is at the end of the file.
            temp.seek(0) # Rewind the file. (0: the beginning of the file)
            self.zip.writestr('annual_harvest_and_timber_product_output_no_caption.png', temp.read(), compress_type=zipfile.ZIP_STORED)
        plt.clf()
        plt.close()
        return

    def generate_big_table_graph(self,big_table,units):
        P = nm.Fields.ppresent
        if(units == "co2e"):
            fig, ax = plt.subplots()
            plt.subplots_adjust(bottom=0.4)
            plt.title('Big Table Results')
            plt.xlabel('Inventory Year')
            txt = "This table compares the collective sum of products in use, emissions, and harvest data in CO2e"
            plt.figtext(0.5, 0.05, txt, wrap=True, horizontalalignment='center', fontsize=12)
            ax.plot(big_table[nm.Fields.harvest_year],big_table[nm.Fields.co2(nm.Fields.primary_product_sum)],label="Primary Products Sum")
            ax.plot(big_table[nm.Fields.harvest_year],big_table[nm.Fields.co2(nm.Fields.products_in_use)],label="Products in Use")
            ax.plot(big_table[nm.Fields.harvest_year],big_table[nm.Fields.co2(P(nm.Fields.swds))],label="SWDS")
            ax.plot(big_table[nm.Fields.harvest_year],big_table[nm.Fields.co2("all_"+nm.Fields.emitted)],label="Emitted")
            ax.plot(big_table[nm.Fields.harvest_year],big_table['accounted'],label="Accounted")
            ax.plot(big_table[nm.Fields.harvest_year],big_table['error'],label="Error")
            Labeloffset(ax, label="Metric Tons CO2E", axis="y")
            ax.legend()
            plt.rcParams["figure.figsize"] = (8,6)
            with tempfile.TemporaryFile(suffix=".png") as temp:
                plt.savefig(temp, format="png", pad_inches=0.1, bbox_inches = "tight") # File position is at the end of the file.
                temp.seek(0) # Rewind the file. (0: the beginning of the file)
                self.zip.writestr('big_table_co2e.png', temp.read(), compress_type=zipfile.ZIP_STORED)
            plt.clf()
            plt.close()
        else:
            fig, ax = plt.subplots()
            plt.subplots_adjust(bottom=0.4)
            plt.title('Big Table Results')
            plt.xlabel('Inventory Year')
            txt = "This table compares the collective sum of products in use, emissions, and harvest data in Megagrams Carbon"
            plt.figtext(0.5, 0.05, txt, wrap=True, horizontalalignment='center', fontsize=12)
            ax.plot(big_table[nm.Fields.harvest_year],big_table[nm.Fields.mgc(nm.Fields.primary_product_sum)],label="Primary Products Sum")
            ax.plot(big_table[nm.Fields.harvest_year],big_table[nm.Fields.mgc(nm.Fields.products_in_use)],label="Products in Use")
            ax.plot(big_table[nm.Fields.harvest_year],big_table[nm.Fields.mgc(P(nm.Fields.swds))],label="SWDS")
            ax.plot(big_table[nm.Fields.harvest_year],big_table[nm.Fields.mgc("all_"+nm.Fields.emitted)],label="Emitted")
            ax.plot(big_table[nm.Fields.harvest_year],big_table['accounted'],label="Accounted")
            ax.plot(big_table[nm.Fields.harvest_year],big_table['error'],label="Error")
            Labeloffset(ax, label="Megagrams Carbon", axis="y")
            ax.legend()
            plt.rcParams["figure.figsize"] = (8,6)
            with tempfile.TemporaryFile(suffix=".png") as temp:
                plt.savefig(temp, format="png", pad_inches=0.1, bbox_inches = "tight") # File position is at the end of the file.
                temp.seek(0) # Rewind the file. (0: the beginning of the file)
                self.zip.writestr('big_table_mgc.png', temp.read(), compress_type=zipfile.ZIP_STORED)
            plt.clf()
            plt.close()

        return

class Labeloffset():
    def __init__(self,  ax, label="", axis="y"):
        self.axis = {"y":ax.yaxis, "x":ax.xaxis}[axis]
        self.label=label
        ax.callbacks.connect(axis+'lim_changed', self.update)
        ax.figure.canvas.draw()
        self.update(None)

    def update(self, lim):
        fmt = self.axis.get_major_formatter()
        self.axis.offsetText.set_visible(False)
        self.axis.set_label_text(self.label + " "+ fmt.get_offset() )