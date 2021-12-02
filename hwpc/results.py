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

        self.timber_products = None
        self.harvests = None
        self.primary_products = None
        self.end_use_products = None
        self.discarded_wood_paper = None
        self.discarded_products = None
        self.dispositions = None

        

        self.working_table = None

        self.total_dispositions = None

        self.burned_captured = None
        
        # Final output collections
        self.annual_timber_products = None
        self.burned = None
        self.composted = None
        self.products_in_use = None
        self.recovered_in_use = None
        self.in_landfills = None
        self.in_dumps = None
        self.fuelwood = None
        self.emissions = None
        self.all_in_use = None
        self.final = None
        self.total_all_dispositions = None

        ##################################

        self.md = model_data.ModelData()
    
        self.zip_buffer = BytesIO()
        
        self.zip = zipfile.ZipFile(self.zip_buffer, mode='w', compression=zipfile.ZIP_STORED, allowZip64=False)

        return

    def save_results(self):
        with tempfile.TemporaryFile() as temp:
            self.working_table.to_csv(temp)
            temp.seek(0)
            self.zip.writestr('results.csv', temp.read(), compress_type=zipfile.ZIP_STORED)
        return
        
    def save_total_dispositions(self):
        results_json = {}

        df = pd.DataFrame(self.working_table)
        final = pd.DataFrame(self.final)
        primary_products = pd.DataFrame(self.primary_products)
        harvests = pd.DataFrame(self.harvests)
        total_in_use = pd.DataFrame(self.all_in_use)
        recycled = pd.DataFrame(self.recovered_in_use)
        total_all_dispositions = pd.DataFrame(self.total_all_dispositions)
        annual_timber_products = pd.DataFrame(self.annual_timber_products)

        # CUMULATIVE DISCARDED PRODUCTS
        cum_products = total_all_dispositions[nm.Fields.c(nm.Fields.products_in_use)]
        self.generate_graph(cum_products,
                        0.4,
                        'Total Cumulative Carbon in End Use Products in Use',
                        'Total cumulative metric tons carbon stored in end-use products in use manufactured from total timber harvested from 1906 to 2018. The recalcitrance of carbon in harvested wood products is highly dependent upon the end use of those products. The carbon remaining in the end-use products in use pool in a given inventory year includes products in use and recovered products.',
                        'total_end_use_products',
                        'Metric Tons C')

        # CUMULATIVE RECOVERED PRODUCTS CARBON
        recycled_carbon = total_all_dispositions[nm.Fields.c(nm.Fields.recovered.lower())]
        self.generate_graph(recycled_carbon,
                        0.3,
                        'Total Cumulative Carbon in Recovered Products in Use',
                        'Total cumulative metric tons carbon stored in recovered products in use manufactured from total timber harvested from 1906 to 2018. Carbon in recovered products in use are recycled wood and paper that reenters the products in use category.',
                        'total_recycled_carbon',
                        'Metric Tons C')

        # CUMULATIVE RECOVERED PRODUCTS CO2E
        recycled_emit = total_all_dispositions[nm.Fields.co2(nm.Fields.recycled)]
        self.generate_graph(recycled_emit,
                        0.4,
                        'Total Cumulative Carbon Emitted from \n Recovered Products',
                        'Total cumulative metric tons carbon emitted from recovered products manufactured from total timber harvested from 1906 to 2018. Carbon emitted from recovered products in use is recycled wood and paper that reenters the products in use category. Carbon emissions are displayed in units of carbon dioxide equivalent (CO2e) and do not include other carbon-based greenhouse gases such as methane.',
                        'total_recycled_carbon_emitted',
                        'Metric Tons CO2e')

        # CUMULATIVE EMIT FROM DISCARD PRODUCTS WITH ENERGY CAPTURE (FUEL)
        # burned_w_energy_capture_emit = burned_w_energy_capture.groupby(by='Year')[nm.Fields.burned_with_energy_capture].sum()
        # self.generate_graph(burned_w_energy_capture_emit,
        #                 0.4,
        #                 'Total Cumulative Carbon Emitted from Burning Discard Products \n with Energy Capture',
        #                 'Total cumulative metric ton carbon emitted from burning discarded products with energy capture manufactured from total timber harvested from 1906 to 2018. Discarded products are assumed to be burned in an incinerator with energy capture. Emmitted carbon is displayed in units of carbon dioxide equivalent (CO2e) and do not include other carbon-based greenhouse gases such as methane.',
        #                 'burned_w_energy_capture_emitted',
        #                 'Metric Tons CO2e')

        # CUMULATIVE EMIT FROM DISCARD PRODUCTS WITH ENERGY CAPTURE (FUEL)
        burned_wo_energy_capture_emit = total_all_dispositions[nm.Fields.burned_wo_energy_capture]
        self.generate_graph(burned_wo_energy_capture_emit,
                        0.4,
                        'Total Cumulative Carbon Emitted from Burning Discard Products \n without Energy Capture',
                        'Total cumulative metric tons carbon emitted from burning discarded products without energy capture manufactured from total timber harvested from 1906 to 2018. Carbon emiited from burned discarded products is assumed to be emitted without energy capture. Carbon emissions are displayed in units of carbon dioxide equivalent (CO2e) and do not include other carbon-based greenhouse gases such as methane.',
                        'burned_wo_energy_capture_emit',
                        'Metric Tons CO2e')

        # CUMULATIVE DISCARD COMPOST CO2E
        composted_emit = total_all_dispositions[nm.Fields.co2(nm.Fields.composted)]
        self.generate_graph(composted_emit,
                        0.5,
                        'Total Cumulative Carbon Emitted from Compost',
                        'Total cumulative metric tons carbon emitted from composted discarded harvested wood products manufactured from total timber harvested from 1906 to 2018. No carbon storage is associated with composted discarded products and all composted carbon is decay emitted without energy capture. Carbon emissions are displayed in units of carbon dioxide equivalent (CO2e) and do not include other greenhouse gases such as methane.',
                        'total_composted_carbon_emitted',
                        'Metric Tons CO2e')

        # CUMULATIVE DISCARD LANDFILL CARBON
        landfills_carbon = total_all_dispositions[nm.Fields.c(nm.Fields.landfills.lower()+"_"+nm.Fields.present)]
        self.generate_graph(landfills_carbon,
                        0.35,
                        'Total Cumulative Carbon in Landfills',
                        'Total cumulative metric tons carbon stored in landfills from discarded products manufactured from total timber harvested from 1906 to 2018. Carbon in landfills are discarded wood and paper products and comprise a portion of the solid waste disposal site pool.',
                        'total_landfills_carbon',
                        'Metric Tons C')

        # CUMULATIVE DISCARD LANDFILL CO2E
        landfills_emit = total_all_dispositions[nm.Fields.co2(nm.Fields.landfills)]
        self.generate_graph(landfills_emit,
                        0.5,
                        'Total Cumulative Carbon Emitted from Landfills',
                        'Total cumulative metric tons carbon emitted from discarded produts in landfills manufactured from total timber harvested from 1906 to 2018. Carbon emitted from discarded wood and paper products in landfills is decay without energy capture. Methane remediation from landfills that includes combustion and subsequent emissions with energy capture is not included. Carbon emissions are displayed in usnits of carbon dioxide equivalent (CO2e) and do not include other carbon-based greenhouse gases such as methane.',
                        'total_landfills_carbon_emitted',
                        'Metric Tons CO2e')
        
        # CUMULATIVE DISCARD DUMPS CARBON
        dumps_carbon = total_all_dispositions[nm.Fields.c(nm.Fields.dumps.lower()+"_"+nm.Fields.present)]
        self.generate_graph(dumps_carbon,
                        0.45,
                        'Total Cumulative Carbon in Dumps',
                        'Total cumulative metric tons carbon stored in dumps from discarded products manufactured from total timber harvested from 1906 to 2018. Carbon in dumps include discarded wood and paper products and comprise a portion of the solid waste disposal site pool. Prior to 1970, wood and paper waste was generally discarded to dumps, as opposed to modern landfills.',
                        'total_dumps_carbon',
                        'Metric Tons C')

        # CUMULATIVE DISCARD DUMPS CO2E
        dumps_emit = total_all_dispositions[nm.Fields.co2(nm.Fields.dumps)]
        self.generate_graph(dumps_emit,
                        0.5,
                        'Total Cumulative Carbon Emitted from Dumps',
                        'Total cumulative metric tons carbon emitted from discarded products in dumps manufactured from total timber harvested from 1906 to 2018. Carbon emitted from discarded wood and paper products in dumps is decay without energy capture. Prior to 1970 wood and paper waste was generally discarded to dumps, where it was subject to higher rates of decay than in modern landfills. Carbon emissions are displayed in units of carbon dioxide equivalent (CO2e) and do not include other carbon-based greenhouse gases such as methane.',
                        'total_dumps_carbon_emitted',
                        'Metric Tons CO2e')
        
        fuelwood_emit = total_all_dispositions[nm.Fields.co2(nm.Fields.burned_with_energy_capture)]
        self.generate_graph(fuelwood_emit,
                        0.5,
                        'Total Cumulative Carbon Emitted from Fuelwood with Energy Capture',
                        'Total cumulative metric tons carbon emitted from fuelwood and wood waste used for fuel with energy capture from total timber harvested from 1906 to 2018. Carbon emitted from burning fuelwood and wood waste with energy capture occurs during the year of harvest and is not assumed to substitute for an equivalent amount of fossil fuel carbon. Carbon emissions are displayed in units of carbon dioxide equivalent (CO2e) and do not include other carbon-based greenhouse gases such as methane.',
                        'total_fuelwood_carbon_emitted',
                        'Metric Tons CO2e')

        # ALL DISPOSITIONS
        with tempfile.TemporaryFile() as temp:
            total_all_dispositions.to_csv(temp)
            temp.seek(0)
            self.zip.writestr('all_dispositions.csv', temp.read(), compress_type=zipfile.ZIP_STORED)

        #PRIMARY PRODUCTS
        with tempfile.TemporaryFile() as temp:
            primary_products.to_csv(temp)
            temp.seek(0)
            self.zip.writestr('primary_products.csv', temp.read(), compress_type=zipfile.ZIP_STORED)

        #CARBON STOCKS
        with tempfile.TemporaryFile() as temp:
            total_in_use.to_csv(temp)
            temp.seek(0)
            self.zip.writestr('total_in_use.csv', temp.read(), compress_type=zipfile.ZIP_STORED)

        products_in_use = total_in_use[nm.Fields.products_in_use+"_"+nm.Fields.carbon]
        with tempfile.TemporaryFile() as temp:
            products_in_use.to_csv(temp)
            temp.seek(0)
            self.zip.writestr('products_in_use.csv', temp.read(), compress_type=zipfile.ZIP_STORED)

        swds = total_in_use[nm.Fields.c(nm.Fields.swds)]
        with tempfile.TemporaryFile() as temp:
            swds.to_csv(temp)
            temp.seek(0)
            self.zip.writestr('swds.csv', temp.read(), compress_type=zipfile.ZIP_STORED)

        fig, ax = plt.subplots()
        plt.subplots_adjust(bottom=0.45)
        plt.title('Total Cumulative Carbon Stocks')
        color = 'tab:red'
        plt.xlabel('Inventory Year')
        
        plt.ticklabel_format(axis='y',style='sci',scilimits=(1,5))
        txt = "Total cumulative metric tons of carbon stocks in harvested wood products (HWP) manufactured from total timber harvested from 1906 to 2018 using the IPCC Tier 3 Production Approach. \n Carbon in HWP includes both products that are still in use and carbon stored at solid waste disposal sites (SWDS)"
        plt.figtext(0.5, 0.05, txt, wrap=True, horizontalalignment='center', fontsize=12, weight='light')
        ax.stackplot(total_all_dispositions.index,final[nm.Fields.c(nm.Fields.products_in_use)].values,final[nm.Fields.c(nm.Fields.swds)].values, colors=("tab:blue","tab:red"),labels=("Products In Use", "SWDS"))
        lo = Labeloffset(ax, label="Total Carbon Stocks Metric Tons", axis="y")
        ax.legend()
        plt.rcParams["figure.figsize"] = (8,6)
        with tempfile.TemporaryFile(suffix=".png") as temp:
            plt.savefig(temp, format="png", pad_inches=0.1, bbox_inches = "tight") # File position is at the end of the file.
            temp.seek(0) # Rewind the file. (0: the beginning of the file)
            self.zip.writestr('total_cumulative_carbon_stocks.png', temp.read(), compress_type=zipfile.ZIP_STORED)
        plt.clf()

        #CARBON CHANGE
        final = pd.DataFrame(self.final)
        with tempfile.TemporaryFile() as temp:
            final.to_csv(temp)
            temp.seek(0)
            self.zip.writestr('final.csv', temp.read(), compress_type=zipfile.ZIP_STORED)
        # We sum products_in_use and swds_change to convert NaN values to 0, even if there is only one per year.
        products_in_use_change = final.groupby(by='Year')[nm.Fields.products_in_use+"_"+nm.Fields.carbon+"_change"].sum()
        swds_change = final.groupby(by='Year')[nm.Fields.swds+"_"+nm.Fields.carbon+"_change"].sum()
        
        fig, ax = plt.subplots()
        plt.subplots_adjust(bottom=0.4)
        plt.title('Annual Net Change in Carbon Stocks')
        color = 'tab:red'
        plt.xlabel('Inventory Year')
        # plt.ylabel('Carbon Stocks Change')
        plt.ticklabel_format(axis='y',style='sci',scilimits=(0,0))
        ax.axhline(0, color='grey', linewidth=0.8)
        ax.set_ylim([min(swds_change), max(swds_change)])
        txt = "Total cumulative metric tons of carbon stocks in harvested wood products (HWP) manufactured from total timber harvested from 1906 to 2018 using the IPCC Tier 3 Production Approach. \n Carbon in HWP includes both products that are still in use and carbon stored at solid waste disposal sites (SWDS)"
        plt.figtext(0.5, 0.05, txt, wrap=True, horizontalalignment='center', fontsize=12)
        p1 = ax.bar(final.index,products_in_use_change,label="Products In Use",color=color)
        color = 'tab:blue'
        p2 = ax.bar(final.index,swds_change, color=color, label="SWDS")
        lo = Labeloffset(ax, label="Metric Tons Carbon", axis="y")
        ax.legend()
        plt.rcParams["figure.figsize"] = (8,6)
        with tempfile.TemporaryFile(suffix=".png") as temp:
            plt.savefig(temp, format="png", pad_inches=0.1, bbox_inches = "tight") # File position is at the end of the file.
            temp.seek(0) # Rewind the file. (0: the beginning of the file)
            self.zip.writestr('annual_net_change_carbon_stocks.png', temp.read(), compress_type=zipfile.ZIP_STORED)
        plt.clf()

        # TOTAL HARVEST AND TIMBER RESULTS
        timber_products_results = annual_timber_products[[nm.Fields.harvest_year, nm.Fields.c(nm.Fields.primary_product_results)]]
        with tempfile.TemporaryFile() as temp:
            timber_products_results.to_csv(temp)
            temp.seek(0)
            self.zip.writestr('annual_timber_product_output.csv', temp.read(), compress_type=zipfile.ZIP_STORED)

        harvests_results = annual_timber_products[nm.Fields.ccf]
        with tempfile.TemporaryFile() as temp:
            harvests_results.to_csv(temp)
            temp.seek(0)
            self.zip.writestr('annual_harvests_output.csv', temp.read(), compress_type=zipfile.ZIP_STORED)
        
        color = 'tab:red'
        fig, ax = plt.subplots()
        plt.subplots_adjust(bottom=0.4)
        plt.title('Annual Harvest and Timber Product Output')
        plt.xlabel('Inventory Year')
        txt = "Annual total timber harvest and product output converted to metric tons of carbon, from 1906 to 2018"
        plt.figtext(0.5, 0.05, txt, wrap=True, horizontalalignment='center', fontsize=12)
        ax.plot(timber_products_results[nm.Fields.harvest_year],timber_products_results[nm.Fields.c(nm.Fields.primary_product_results)], color=color,label="Timber Product Output (Metric Tons C)")
        color = 'tab:blue'
        ax.plot(timber_products_results[nm.Fields.harvest_year],harvests_results, color=color,label="Annual Harvest (MBF)")
        lo = Labeloffset(ax, label="Metric Tons Carbon", axis="y")
        ax.legend()
        plt.rcParams["figure.figsize"] = (8,6)
        with tempfile.TemporaryFile(suffix=".png") as temp:
            plt.savefig(temp, format="png", pad_inches=0.1, bbox_inches = "tight") # File position is at the end of the file.
            temp.seek(0) # Rewind the file. (0: the beginning of the file)
            self.zip.writestr('annual_harvest_and_timber_product_output.png', temp.read(), compress_type=zipfile.ZIP_STORED)
        # results_json["total_end_use_products.csv"] = nm.Output.output_path + '/results/total_end_use_products.csv'
        # results_json["total_end_use_products.png"] = nm.Output.output_path + '/results/total_end_use_products.png'
        plt.show()
        plt.clf()
        

        self.zip_buffer.seek(0)

        print('Output Path:', nm.Output.output_path)
        print('Run Name:', nm.Output.run_name)

        gch.upload_temp('hwpcarbon-data', self.zip_buffer, nm.Output.output_path + '/results/' + nm.Output.run_name + '.zip', 'application/zip')

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

    def generate_graph(self,data_frame,adjust_bottom,title,txt,file_name,y_axis):

        with tempfile.TemporaryFile() as temp:
            data_frame.to_csv(temp)
            temp.seek(0)
            self.zip.writestr(file_name+'.csv', temp.read(), compress_type=zipfile.ZIP_STORED)
            fig, ax = plt.subplots()
        plt.subplots_adjust(bottom = adjust_bottom)
        plt.title(title, multialignment='center')
        plt.xlabel('Inventory Year')
        
        if(title=="Total Cumulative Carbon Emitted from Burning Discard Products \n with Energy Capture"):
           plt.ylim(-1,1) 
        ax.plot(data_frame)
        plt.ticklabel_format(axis='y',style='sci',scilimits=(1,5))
        plt.figtext(0.5, 0.05, txt, wrap=True, horizontalalignment='center', fontsize=12)
        lo = Labeloffset(ax, label=y_axis, axis="y")
        plt.rcParams["figure.figsize"] = (8,6)
        with tempfile.TemporaryFile(suffix=".png") as temp:
            plt.savefig(temp, format="png", pad_inches=0.1) # File position is at the end of the file.
            temp.seek(0) # Rewind the file. (0: the beginning of the file)
            self.zip.writestr(file_name+'.png', temp.read(), compress_type=zipfile.ZIP_STORED)
        #results_json["total_dumps_carbon_emitted.csv"] = nm.Output.output_path + '/results/total_dumps_carbon_emitted.csv'
        #results_json["total_dumps_carbon_emitted.png"] = nm.Output.output_path + '/results/total_dumps_carbon_emitted.png'
        plt.clf()


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