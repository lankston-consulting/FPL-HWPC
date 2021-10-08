from io import BytesIO
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json
import os
import tempfile
import zipfile

from config import gch
from hwpc import model_data
from hwpc.names import Names as nm
from utils import pickler



class Results(pickler.Pickler):

    def __init__(self) -> None:
        super().__init__()

        self.timber_products = None
        self.harvests = None
        self.primary_products = None
        self.end_use_products = None
        self.products_in_use = None
        self.discarded_products = None
        self.discarded_wood_paper = None
        self.dispositions = None

        self.working_table = None

        self.total_dispositions = None

        self.burned_captured = None

        self.md = model_data.ModelData()
    
        self.zip_buffer = BytesIO()
        
        self.zip = zipfile.ZipFile(self.zip_buffer, mode='a')

        return

    def save_results(self):
        with tempfile.TemporaryFile() as temp:
            self.working_table.to_csv(temp)
            temp.seek(0)
            self.zip.writestr('results.csv', temp.read())
        return
        
    def save_total_dispositions(self):
        results_json = {}

        df = pd.DataFrame(self.working_table)
        timber_products = pd.DataFrame(self.timber_products)
        harvests = pd.DataFrame(self.harvests)
        burned = df[df[nm.Fields.discard_destination_id] == 0] 
        burned_w_energy_capture = burned[burned[nm.Fields.fuel]==1]
        burned_wo_energy_capture = burned[burned[nm.Fields.fuel]==0]
        recycled = df[df[nm.Fields.discard_destination_id] == 1]
        composted = df[df[nm.Fields.discard_destination_id] == 2]
        landfills = df[df[nm.Fields.discard_destination_id] == 3]
        dumps = df[df[nm.Fields.discard_destination_id] == 4]

        # burned = burned.groupby(by='Year')[['discarded_products_adjusted','DiscardDestinationRatio']]
        # burned = burned.agg(burned)
        # burned.to_csv('total_dispositions_0.csv')
        # plt.title('Total Cumulative Carbon in End Use Products in Use')
        # plt.xlabel('Years')
        # plt.ylabel('Metric Tons C (10^6)')
        # plt.plot(burned)
        # plt.show()

        # CUMULATIVE DISCARDED PRODUCTS
        cum_products = df.groupby(by='Year')[nm.Fields.running_discarded_products].sum()
        with tempfile.TemporaryFile() as temp:
            cum_products.to_csv(temp)
            temp.seek(0)
            self.zip.writestr('total_end_use_products.csv', temp.read())
        
        # TOTAL HARVEST AND TIMBER RESULTS
        timber_products_results = timber_products.groupby(by='Year')[nm.Fields.timber_product_results].sum()
        with tempfile.TemporaryFile() as temp:
            timber_products_results.to_csv(temp)
            temp.seek(0)
            self.zip.writestr('annual_timber_product_output.csv', temp.read())

        harvests_results = timber_products[[nm.Fields.harvest_year, nm.Fields.ccf]]
        with tempfile.TemporaryFile() as temp:
            harvests_results.drop_duplicates().sort_values(nm.Fields.harvest_year).to_csv(temp)
            temp.seek(0)
            self.zip.writestr('annual_harvests_output.csv', temp.read())

        # Defunct code for generating pdfs    
        # with tempfile.NamedTemporaryFile() as temp:
        #     cum_products.to_csv(temp)
        #     temp.seek(0)
        #     #print(os.path.dirname(temp.name))
        #     output = pypandoc.convert_file(temp.name, 'pdf', outputfile="total_end_use_products.pdf")
        #     assert output == ""
        #     self.zip.writestr('total_end_use_products.pdf', output)
            
        plt.subplots_adjust(bottom=0.4)
        plt.title('Total Cumulative Carbon in End Use Products in Use')
        plt.xlabel('Inventory Year')
        plt.ylabel('Metric Tons C')
        plt.ticklabel_format(axis='y',style='sci',scilimits=(1,5))
        txt = "Figure. Total cumulative metric tons carbon stored in end-use products in use manufactured from total timber harvested in ppd from 1906 to 2018. The recalcitrance of carbon in harvested wood products is highly dependent upon the end use of those products. The carbon remaining in the end-use products in use pool in a given inventory year includes products in use and recovered products."
        plt.figtext(0.5, 0.05, txt, wrap=True, horizontalalignment='center', fontsize=12, weight='light')
        plt.plot(cum_products)
        with tempfile.TemporaryFile(suffix=".png") as temp:
            plt.savefig(temp, format="png", pad_inches=0.1) # File position is at the end of the file.
            temp.seek(0) # Rewind the file. (0: the beginning of the file)
            self.zip.writestr('total_end_use_products.png', temp.read())
        #plt.savefig('results/total_end_use_products',pad_inches=0.1)
        #gch.upload_blob('hwpcarbon-data','results/total_end_use_products.csv', nm.Output.output_path + '/results/total_end_use_products.csv')
        #gch.upload_blob('hwpcarbon-data','results/total_end_use_products.png', nm.Output.output_path + '/results/total_end_use_products.png')
        
        results_json["total_end_use_products.csv"] = nm.Output.output_path + '/results/total_end_use_products.csv'
        results_json["total_end_use_products.png"] = nm.Output.output_path + '/results/total_end_use_products.png'
        plt.clf()

        # CUMULATIVE RECOVERED PRODUCTS CARBON
        recycled_carbon = recycled.groupby(by='Year')[nm.Fields.carbon].sum()
        with tempfile.TemporaryFile() as temp:
            recycled_carbon.to_csv(temp)
            temp.seek(0)
            self.zip.writestr('total_recycled_carbon.csv', temp.read())
        plt.subplots_adjust(bottom=0.4)
        plt.title('Total Cumulative Carbon in Recovered Products in Use')
        plt.xlabel('Inventory Year')
        plt.ylabel('Metric Tons C')
        plt.plot(recycled_carbon)
        plt.ticklabel_format(axis='y',style='sci',scilimits=(1,5))
        txt = "Figure. Total cumulative metric tons carbon stored in recovered products in use manufactured from total timber harvested in ppd from 1906 to 2018. Carbon in recovered products in use are recycled wood and paper that reenters the products in use category."
        plt.figtext(0.5, 0.05, txt, wrap=True, horizontalalignment='center', fontsize=12)
        with tempfile.TemporaryFile(suffix=".png") as temp:
            plt.savefig(temp, format="png", pad_inches=0.1) # File position is at the end of the file.
            temp.seek(0) # Rewind the file. (0: the beginning of the file)
            self.zip.writestr('total_recycled_carbon.png', temp.read())
        #plt.savefig('results/total_recycled_carbon')
        # gch.upload_blob('hwpcarbon-data','results/total_recycled_carbon.csv', nm.Output.output_path + '/results/total_recycled_carbon.csv')
        # gch.upload_blob('hwpcarbon-data','results/total_recycled_carbon.png', nm.Output.output_path + '/results/total_recycled_carbon.png')
        # self.zip.write('results/total_recycled_carbon.png',arcname='total_recycled_carbon.png')
        # self.zip.write('results/total_recycled_carbon.csv',arcname='total_recycled_carbon.csv')
        results_json["total_recycled_carbon.csv"] = nm.Output.output_path + '/results/total_recycled_carbon.csv'
        results_json["total_recycled_carbon.png"] = nm.Output.output_path + '/results/total_recycled_carbon.png'
        plt.clf()

        # CUMULATIVE RECOVERED PRODUCTS CO2E
        recycled_emit = recycled.groupby(by='Year')[nm.Fields.co2].sum()
        with tempfile.TemporaryFile() as temp:
            recycled_carbon.to_csv(temp)
            temp.seek(0)
            self.zip.writestr('total_recycled_carbon_emitted.csv', temp.read())
        plt.subplots_adjust(bottom=0.4)
        plt.title('Total Cumulative Carbon Emitted from Recovered Products')
        plt.xlabel('Inventory Year')
        plt.ylabel('Metric Tons CO2e')
        plt.plot(recycled_emit)
        plt.ticklabel_format(axis='y',style='sci',scilimits=(1,5))
        txt = "Figure. Total cumulative metric tons carbon emitted from recovered products manufactured from total timber harvested in ppd from 1906 to 2018. Carbon emitted from recovered products in use is recycled wood and paper that reenters the products in use category. Carbon emissions are displayed in units of carbon dioxide equivalent (CO2e) and do not include other carbon-based greenhouse gases such as methane."
        plt.figtext(0.5, 0.05, txt, wrap=True, horizontalalignment='center', fontsize=12)
        with tempfile.TemporaryFile(suffix=".png") as temp:
            plt.savefig(temp, format="png", pad_inches=0.1) # File position is at the end of the file.
            temp.seek(0) # Rewind the file. (0: the beginning of the file)
            self.zip.writestr('total_recycled_carbon_emitted.png', temp.read())
        results_json["total_recycled_carbon_emitted.csv"] = nm.Output.output_path + '/results/total_recycled_carbon_emitted.csv'
        results_json["total_recycled_carbon_emitted.png"] = nm.Output.output_path + '/results/total_recycled_carbon_emitted.png'
        plt.clf()

        # CUMULATIVE EMIT FROM DISCARD PRODUCTS WITH ENERGY CAPTURE (FUEL)
        burned_w_energy_capture_emit = burned_w_energy_capture.groupby(by='Year')[nm.Fields.co2].sum()
        with tempfile.TemporaryFile() as temp:
            burned_w_energy_capture_emit.to_csv(temp)
            temp.seek(0)
            self.zip.writestr('burned_w_energy_capture_emmited.csv', temp.read())
        plt.subplots_adjust(bottom=0.4)
        plt.title('Total Cumulative Carbon Emitted from Burning Discard Products \n with Energy Capture', multialignment='center')
        plt.xlabel('Inventory Year')
        plt.ylabel('Metric Tons CO2e')
        plt.plot(burned_w_energy_capture_emit)
        plt.ylim(-1,1)
        plt.ticklabel_format(axis='y',style='sci',scilimits=(1,5))
        txt = "Total cumulative metric ton carbon emitted from burning discarded products with energy capture manufactured from total timber harvested in ppd from 1906 to 2018. Discarded products are assumed to be burned in an incinerator with energy capture. Emmitted carbon is displayed in units of carbon dioxide equivalent (CO2e) and do not include other carbon-based greenhouse gases such as methane."
        plt.figtext(0.5, 0.05, txt, wrap=True, horizontalalignment='center', fontsize=12)
        with tempfile.TemporaryFile(suffix=".png") as temp:
            plt.savefig(temp, format="png", pad_inches=0.1) # File position is at the end of the file.
            temp.seek(0) # Rewind the file. (0: the beginning of the file)
            self.zip.writestr('burned_w_energy_capture_emitted.png', temp.read())
        results_json["burned_w_energy_capture_emitted.csv"] = nm.Output.output_path + '/results/burned_w_energy_capture_emitted.csv'
        results_json["burned_w_energy_capture_emitted.png"] = nm.Output.output_path + '/results/burned_w_energy_capture_emitted.png'
        plt.clf()

        # CUMULATIVE EMIT FROM DISCARD PRODUCTS WITH ENERGY CAPTURE (FUEL)
        burned_wo_energy_capture_emit = burned_wo_energy_capture.groupby(by='Year')[nm.Fields.co2].sum()
        with tempfile.TemporaryFile() as temp:
            burned_wo_energy_capture_emit.to_csv(temp)
            temp.seek(0)
            self.zip.writestr('burned_wo_energy_capture_emit.csv', temp.read())
        plt.subplots_adjust(bottom=0.4)
        plt.title('Total Cumulative Carbon Emitted from Burning Discard Products \n without Energy Capture', multialignment='center')
        plt.xlabel('Inventory Year')
        plt.ylabel('Metric Tons CO2e')
        plt.plot(burned_wo_energy_capture_emit)
        plt.ticklabel_format(axis='y',style='sci',scilimits=(1,5))
        txt = "Total cumulative metric tons carbon emitted from burning discarded products without energy capture manufactured from total timber harvested in ppd from 1906 to 2018. Carbon emiited from burned discarded products is assumed to be emitted without energy capture. Carbon emissions are displayed in units of carbon dioxide equivalent (CO2e) and do not include other carbon-based greenhouse gases such as methane."
        plt.figtext(0.5, 0.05, txt, wrap=True, horizontalalignment='center', fontsize=12)
        with tempfile.TemporaryFile(suffix=".png") as temp:
            plt.savefig(temp, format="png", pad_inches=0.1) # File position is at the end of the file.
            temp.seek(0) # Rewind the file. (0: the beginning of the file)
            self.zip.writestr('burned_wo_energy_capture_emit.png', temp.read())
        results_json["burned_wo_energy_capture_emit.csv"] = nm.Output.output_path + '/results/burned_wo_energy_capture_emit.csv'
        results_json["burned_wo_energy_capture_emit.png"] = nm.Output.output_path + '/results/burned_wo_energy_capture_emit.png'
        plt.clf()

        # CUMULATIVE DISCARD COMPOST CO2E
        composted_emit = composted.groupby(by='Year')[nm.Fields.co2].sum()
        with tempfile.TemporaryFile() as temp:
            recycled_carbon.to_csv(temp)
            temp.seek(0)
            self.zip.writestr('total_composted_carbon_emitted.csv', temp.read())
        plt.subplots_adjust(bottom=0.5)
        plt.title('Total Cumulative Carbon Emitted from Compost')
        plt.xlabel('Inventory Year')
        plt.ylabel('Metric Tons CO2e')
        plt.ticklabel_format(axis='y',style='sci',scilimits=(1,5))
        plt.plot(composted_emit)
        txt = "Figure. Total cumulative metric tons carbon emitted from composted discarded harvested wood products manufactured from total timber harvested in ppd from 1906 to 2018. No carbon storage is associated with composted discarded products and all composted carbon is decay emitted without energy capture. Carbon emissions are displayed in units of carbon dioxide equivalent (CO2e) and do not include other greenhouse gases such as methane."
        plt.figtext(0.5, 0.05, txt, wrap=True, horizontalalignment='center', fontsize=12)
        with tempfile.TemporaryFile(suffix=".png") as temp:
            plt.savefig(temp, format="png", pad_inches=0.1) # File position is at the end of the file.
            temp.seek(0) # Rewind the file. (0: the beginning of the file)
            self.zip.writestr('total_composted_carbon_emitted.png', temp.read())
        results_json["total_composted_carbon_emitted.csv"] = nm.Output.output_path + '/results/total_composted_carbon_emitted.csv'
        results_json["total_composted_carbon_emitted.png"] = nm.Output.output_path + '/results/total_composted_carbon_emitted.png'
        plt.clf()

        # CUMULATIVE DISCARD LANDFILL CARBON
        landfills_carbon = landfills.groupby(by='Year')[nm.Fields.carbon].sum()
        with tempfile.TemporaryFile() as temp:
            recycled_carbon.to_csv(temp)
            temp.seek(0)
            self.zip.writestr('total_landfills_carbon.csv', temp.read())
        plt.subplots_adjust(bottom=0.4)
        plt.title('Total Cumulative Carbon in Landfills')
        plt.xlabel('Inventory Year')
        plt.ylabel('Metric Tons C')
        plt.plot(landfills_carbon)
        plt.ticklabel_format(axis='y',style='sci',scilimits=(1,5))
        txt = "Figure. Total cumulative metric tons carbon stored in landfills from discarded products manufactured from total timber harvested in ppd from 1906 to 2018. Carbon in landfills are discarded wood and paper products and comprise a portion of the solid waste disposal site pool."
        plt.figtext(0.5, 0.05, txt, wrap=True, horizontalalignment='center', fontsize=12)
        with tempfile.TemporaryFile(suffix=".png") as temp:
            plt.savefig(temp, format="png", pad_inches=0.1) # File position is at the end of the file.
            temp.seek(0) # Rewind the file. (0: the beginning of the file)
            self.zip.writestr('total_landfills_carbon.png', temp.read())
        results_json["total_landfills_carbon.csv"] = nm.Output.output_path + '/results/total_landfills_carbon.csv'
        results_json["total_landfills_carbon.png"] = nm.Output.output_path + '/results/total_landfills_carbon.png'
        plt.clf()

        # CUMULATIVE DISCARD LANDFILL CO2E
        landfills_emit = landfills.groupby(by='Year')[nm.Fields.co2].sum()
        with tempfile.TemporaryFile() as temp:
            recycled_carbon.to_csv(temp)
            temp.seek(0)
            self.zip.writestr('total_landfills_carbon_emitted.csv', temp.read())
        plt.subplots_adjust(bottom=0.45)
        plt.title('Total Cumulative Carbon Emitted from Landfills')
        plt.xlabel('Inventory Year')
        plt.ylabel('Metric Tons CO2e')
        plt.plot(landfills_emit)
        plt.ticklabel_format(axis='y',style='sci',scilimits=(1,5))
        txt = "Figure. Total cumulative metric tons carbon emitted from discarded produts in landfills manufactured from total timber harvested in ppd from 1906 to 2018. Carbon emitted from discarded wood and paper products in landfills is decay without energy capture. Methane remediation from landfills that includes combustion and subsequent emissions with energy capture is not included. Carbon emissions are displayed in usnits of carbon dioxide equivalent (CO2e) and do not include other carbon-based greenhouse gases such as methane."
        plt.figtext(0.5, 0.05, txt, wrap=True, horizontalalignment='center', fontsize=12)
        with tempfile.TemporaryFile(suffix=".png") as temp:
            plt.savefig(temp, format="png", pad_inches=0.1) # File position is at the end of the file.
            temp.seek(0) # Rewind the file. (0: the beginning of the file)
            self.zip.writestr('total_landfills_carbon_emitted.png', temp.read())
        results_json["total_landfills_carbon_emitted.csv"] = nm.Output.output_path + '/results/total_landfills_carbon_emitted.csv'
        results_json["total_landfills_carbon_emitted.png"] = nm.Output.output_path + '/results/total_landfills_carbon_emitted.png'
        plt.clf()
        
        # CUMULATIVE DISCARD DUMPS CARBON
        dumps_carbon = dumps.groupby(by='Year')[nm.Fields.carbon].sum()
        with tempfile.TemporaryFile() as temp:
            recycled_carbon.to_csv(temp)
            temp.seek(0)
            self.zip.writestr('total_dumps_carbon.csv', temp.read())
        plt.subplots_adjust(bottom=0.4)
        plt.title('Total Cumulative Carbon in Dumps')
        plt.xlabel('Inventory Year')
        plt.ylabel('Metric Tons C')
        plt.plot(dumps_carbon)
        plt.ticklabel_format(axis='y',style='sci',scilimits=(1,5))
        txt = "Figure. Total cumulative metric tons carbon stored in dumps from discarded products manufactured from total timber harvested in ppd from 1906 to 2018. Carbon in dumps include discarded wood and paper products and comprise a portion of the solid waste disposal site pool. Prior to 1970, wood and paper waste was generally discarded to dumps, as opposed to modern landfills."
        plt.figtext(0.5, 0.05, txt, wrap=True, horizontalalignment='center', fontsize=12)
        with tempfile.TemporaryFile(suffix=".png") as temp:
            plt.savefig(temp, format="png", pad_inches=0.1) # File position is at the end of the file.
            temp.seek(0) # Rewind the file. (0: the beginning of the file)
            self.zip.writestr('total_dumps_carbon.png', temp.read())
        results_json["total_dumps_carbon.csv"] = nm.Output.output_path + '/results/total_dumps_carbon.csv'
        results_json["total_dumps_carbon.png"] = nm.Output.output_path + '/results/total_dumps_carbon.png'
        plt.clf()

        # CUMULATIVE DISCARD DUMPS CO2E
        dumps_emit = dumps.groupby(by='Year')[nm.Fields.co2].sum()
        with tempfile.TemporaryFile() as temp:
            recycled_carbon.to_csv(temp)
            temp.seek(0)
            self.zip.writestr('total_dumps_carbon_emitted.csv', temp.read())
        plt.subplots_adjust(bottom=0.45)
        plt.title('Total Cumulative Carbon Emitted from Dumps')
        plt.xlabel('Inventory Year')
        plt.ylabel('Metric Tons C')
        plt.plot(dumps_emit)
        plt.ticklabel_format(axis='y',style='sci',scilimits=(1,5))
        txt = "Figure. Total cumulative metric tons carbon emitted from discarded products in dumps manufactured from total timber harvested in ppd from 1906 to 2018. Carbon emitted from discarded wood and paper products in dumps is decay without energy capture. Prior to 1970 wood and paper waste was generally discarded to dumps, where it was subject to higher rates of decay than in modern landfills. Carbon emissions are displayed in units of carbon dioxide equivalent (CO2e) and do not include other carbon-based greenhouse gases such as methane."
        plt.figtext(0.5, 0.05, txt, wrap=True, horizontalalignment='center', fontsize=12)
        with tempfile.TemporaryFile(suffix=".png") as temp:
            plt.savefig(temp, format="png", pad_inches=0.1) # File position is at the end of the file.
            temp.seek(0) # Rewind the file. (0: the beginning of the file)
            self.zip.writestr('total_dumps_carbon_emitted.png', temp.read())
        results_json["total_dumps_carbon_emitted.csv"] = nm.Output.output_path + '/results/total_dumps_carbon_emitted.csv'
        results_json["total_dumps_carbon_emitted.png"] = nm.Output.output_path + '/results/total_dumps_carbon_emitted.png'
        plt.clf()

        self.zip_buffer.seek(0)

        gch.upload_temp('hwpcarbon-data', self.zip_buffer, nm.Output.output_path + '/results/results.zip')

        self.zip.close()
        self.zip_buffer.close()

        # with open('results/results.json', 'w') as outfile:
        #     json.dump(results_json, outfile)

        # gch.upload_blob('hwpcarbon-data','results/results.json', nm.Output.output_path + '/results/results.json')
        # self.total_dispositions.to_csv('results/total_dispositions.csv')
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
        n = nm.Fields.c(nm.Fields.timber_product_results)
        print(df)
        # df[n] = df[nm.Fields.timber_product_results] * df[nm.Fields.conversion_factor]
        # df_sum = df.groupby(by=nm.Fields.harvest_year)[n].mode()


        return
