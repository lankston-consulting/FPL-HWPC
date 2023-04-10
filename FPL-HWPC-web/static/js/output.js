let output = {};

let captions_dict = [];
let data_dict = [];
let data_bucket = "";
let data_file_name = "";
let harvestmaxDateYear = "";
let harvestminDateYear = "";
let needs_single_year_title = false
let deliver_scenario_json = ""
captions_dict["annual_harvest_and_timber_product_output"] = [
  {
    text: "Annual total timber harvest and product output converted to metric tons of carbon, from [minimum year] to [maximum year].",
  },
];
captions_dict["annual_net_change_carbon_stocks"] = [
  {
    text: "Total cumulative metric tons of carbon stocks in harvested wood products (HWP) manufactured from total timber harvested from [minimum year] to [maximum year] using the IPCC Tier 3 Production Approach. Carbon in HWP includes both products that are still in use and carbon stored at solid waste disposal sites (SWDS). Carbon emission are displayed in units of carbon dioxide equivalent (t CO<sub>2</sub>e) and do not include other carbon-based greenhouse gases such as methane.",
  },
];
captions_dict["all_results_final"] = [
  {
    text: "Total cumulative metric tons of carbon stocks in harvested wood products (HWP) manufactured from total timber harvested from [minimum year] to [maximum year] using the IPCC Tier 3 Production Approach and Total cumulative metric tons carbon emitted with and without energy capture. Carbon in HWP includes both products that are still in use and carbon stored at solid waste disposal sites. Carbon emitted from discarded wood and paper products from landfills is emitted without energy capture. Storage is converted into CO2e and Carbon emissions are displayed in units of carbon dioxide equivalent (t CO<sub>2</sub>e) and do not include other carbon-based greenhouse gases such as methane.",
  },
];
captions_dict["end_use"] = [
  {
    text: "Total cumulative metric tons Carbon stored in End Use Products in Use manufactured from total timber harvested from [minimum year] to [maximum year].",
  },
];
captions_dict["burned_with_energy_capture_emissions"] = [
  {
    text: "Total cumulative metric ton carbon emitted from burning discarded products with energy capture manufactured from total timber harvested from [minimum year] to [maximum year]. Discarded products are assumed to be burned in an incinerator with energy capture. Emitted carbon is displayed in units of carbon dioxide equivalent (t CO<sub>2</sub>e) and do not include other carbon-based greenhouse gases such as methane.",
  },
];
captions_dict["burned_without_energy_capture_emissions"] = [
  {
    text: "Total cumulative metric tons CO<sub>2</sub>e emitted from burning discarded products without energy capture manufactured from total timber harvested from [minimum year] to [maximum year]. Carbon emitted from burned discarded products is assumed to be emitted without energy capture. Carbon emissions are displayed in units of carbon dioxide equivalent (t CO<sub>2</sub>e) and do not include other carbon-based greenhouse gases such as methane.",
  },
];
captions_dict["total_cumulative_carbon_stocks"] = [
  {
    text: "Total cumulative metric tons of carbon stocks in harvested wood products (HWP) manufactured from total timber harvested from [minimum year] to [maximum year] using the IPCC Tier 3 Production Approach. Carbon in HWP includes both products that are still in use and carbon stored at solid waste disposal sites (SWDS).",
  },
];
captions_dict["total_dumps_carbon"] = [
  {
    text: "Total cumulative metric tons Carbon stored in dumps from discarded products manufactured from total timber harvested from [minimum year] to [maximum year]. Carbon in dumps include discarded wood and paper products and comprise a portion of the solid waste disposal site pool. Prior to 1970, wood and paper waste was generally discarded to dumps, as opposed to modern landfills. Carbon emissions are displayed in units of carbon dioxide equivalent (t CO<sub>2</sub>e) and do not include other carbon-based greenhouse gases such as methane.",
  },
];
captions_dict["total_landfills_carbon"] = [
  {
    text: "Total cumulative metric tons Carbon stored in landfills from discarded products manufactured from total timber harvested from [minimum year] to [maximum year]. Carbon in landfills are discarded wood and paper products and comprise a portion of the solid waste disposal site pool. Carbon emissions are displayed in units of carbon dioxide equivalent (t CO<sub>2</sub>e) and do not include other carbon-based greenhouse gases such as methane.",
  },
];
captions_dict["total_dumps_carbon_emitted"] = [
  {
    text: "Total cumulative metric tons CO<sub>2</sub>e emitted from discarded products in dumps manufactured from total timber harvested from [minimum year] to [maximum year]. Carbon emitted from discarded wood and paper products in dumps is decay without energy capture. Prior to 1970 wood and paper waste was generally discarded to dumps, where it was subject to higher rates of decay than in modern landfills. Carbon emissions are displayed in units of carbon dioxide equivalent (t CO<sub>2</sub>e) and do not include other carbon-based greenhouse gases such as methane.",
  },
];
captions_dict["total_composted_carbon_emitted"] = [
  {
    text: "Total cumulative metric tons CO<sub>2</sub>e emitted from composted discarded harvested wood products manufactured from total timber harvested from [minimum year] to [maximum year]. No carbon storage is associated with composted discarded products and all composted carbon is decay emitted without energy capture. Carbon emissions are displayed in units of carbon dioxide equivalent (t CO<sub>2</sub>e) and do not include other greenhouse gases such as methane.",
  },
];
captions_dict["total_landfills_carbon_emitted"] = [
  {
    text: "Total cumulative metric tons CO<sub>2</sub>e emitted from discarded products in landfills manufactured from total timber harvested from [minimum year] to [maximum year]. Carbon emitted from discarded wood and paper products in landfills is decay without energy capture. Methane remediation from landfills that includes combustion and subsequent emissions with energy capture is not included. Carbon emissions are displayed in units of carbon dioxide equivalent (t CO<sub>2</sub>e) and do not include other carbon-based greenhouse gases such as methane.",
  },
];
captions_dict["total_solid_carbon_dispositions"] = [
  {
    text: "Total cumulative metric tons Carbon stored in end-use products in use, in landfills from discarded products, and in dumps from discarded products manufactured from total timber harvested from [minimum year] to [maximum year]. The recalcitrance of carbon in harvested wood products is highly dependent upon the end use of those products. The carbon remaining in the end-use products in use pool in a given inventory year includes products in use and recovered products. Carbon in landfills and dumps are discarded wood and paper products, and comprise a portion of the solid waste disposal site pool. Prior to 1970, wood and paper waste was generally discarded to dumps, as opposed to modern landfills. Stocks are converted into metric tons CO<sub>2</sub>e units.",
  },
];
captions_dict["total_solid_carbon_dispositions2"] = [
  {
    text: "Total cumulative metric tons Carbon stored in end-use products in use, in landfills from discarded products, and in dumps from discarded products manufactured from total timber harvested from [minimum year] to [maximum year]. The recalcitrance of carbon in harvested wood products is highly dependent upon the end use of those products. The carbon remaining in the end-use products in use pool in a given inventory year includes products in use and recovered products. Carbon in landfills and dumps are discarded wood and paper products, and comprise a portion of the solid waste disposal site pool. Prior to 1970, wood and paper waste was generally discarded to dumps, as opposed to modern landfills. Stocks are converted into metric tons CO<sub>2</sub>e units.",
  },
];
captions_dict["total_emissions_dispositions"] = [
  {
    text: "Total cumulative metric tons CO<sub>2</sub>e emitted from fuelwood and wood waste used for fuel with energy capture, burned discarded products with and without energy capture, composted discarded harvested wood products, and discarded products in dumps and landfills manufactured from total timber harvested from [minimum year] to [maximum year]. Carbon emitted from burning fuelwood and wood waste with energy capture occurs during the year of harvest and is not assumed to substitute for an equivalent amount of fossil fuel carbon. Discarded burned products are assumed to be burned in an incinerator with energy capture. No carbon storage is associated with composted discarded products and all composted carbon is decay emitted without energy capture. Carbon emitted from discarded wood and paper products in dumps and landfills is decay without energy capture. Prior to 1970 wood and paper waste was generally discarded to dumps, where it was subject to higher rates of decay than in modern landfills. Carbon emissions are displayed in units of carbon dioxide equivalent (t CO<sub>2</sub>e) and do not include other carbon-based greenhouse gases such as methane.",
  },
];
captions_dict["total_emissions_dispositions2"] = [
  {
    text: "Total cumulative metric tons CO<sub>2</sub>e emitted from fuelwood and wood waste used for fuel with energy capture, burned discarded products with and without energy capture, composted discarded harvested wood products, and discarded products in dumps and landfills manufactured from total timber harvested from [minimum year] to [maximum year]. Carbon emitted from burning fuelwood and wood waste with energy capture occurs during the year of harvest and is not assumed to substitute for an equivalent amount of fossil fuel carbon. Discarded burned products are assumed to be burned in an incinerator with energy capture. No carbon storage is associated with composted discarded products and all composted carbon is decay emitted without energy capture. Carbon emitted from discarded wood and paper products in dumps and landfills is decay without energy capture. Prior to 1970 wood and paper waste was generally discarded to dumps, where it was subject to higher rates of decay than in modern landfills. Carbon emissions are displayed in units of carbon dioxide equivalent (t CO<sub>2</sub>e) and do not include other carbon-based greenhouse gases such as methane.",
  },
];
captions_dict["swds_emissions"] = [
  {
    text: "Total cumulative metric tons CO<sub>2</sub>e emitted from discarded products in landfills and dumps manufactured from total timber harvested from [minimum year] to [maximum year]. Carbon emitted from discarded wood and paper products in landfills and dumps is decay without energy capture. Methane remediation from landfills that includes combustion and subsequent emissions with energy capture is not included. Prior to 1970 wood and paper waste was generally discarded to dumps, where it was subject to higher rates of decay than in modern landfills. Carbon emissions are displayed in units of carbon dioxide equivalent (t CO<sub>2</sub>e) and do not include other carbon-based greenhouse gases such as methane.",
  },
];
// COLORS

const colors = {
  darkBlue: "#1344D6",
  lightBlue: "#80C9D8",
  green: "#00A300",
  darkRed: "#950000",
  lightRed: "#DFA9A9",

  landfill_emissions: "#007500",
  dump_emissions: "#94C973",
  compost_emissions: "#F28A80",
  fuelwood_emissions: "#B43930",


}

let header_dict = [];

header_dict["annual_timber_harvest_table"] = ["Year", "CCF MgC", "End Use MgC"];
header_dict["total_yearly_net_change"] = ["Year", "SWDS Present Change MgC"];
header_dict["total_selected_net_change"] = [
  "Year",
  "New Products in Use MgC",
  "Reused Products in Use MgC",
  "SWDS MgC",
  "New Products in Use Change MgC",
  "Reused Products in Use Change MgC",
  "SWDS Change MgC",
];
header_dict["total_selected_net_change2"] = [
  "Year",
  "Products in Use MgC",
  // "Reused Products in Use MgC",
  "SWDS MgC",
  "Products in Use Change MgC",
  // "Reused Products in Use Change MgC",
  "SWDS Change MgC",
];
header_dict["total_yearly_dispositions"] = [
  // "Year",
  // "SWDS Present Change MgC",
  // "Emitted with Energy Capture CO2e",
  // "Emitted with Energy Capture Change CO2e",
  // "Emitted without Energy Capture CO2e",
  // "Emitted without Energy Capture Change CO2e",
  // "Products in Use Change Mgc",
  // "SWDS MgC",
  // "SWDS Change MgC",
  // "Total Remaining MgC",
  // "Total Change MgC",
  // "Present Change MgC"

  "Year",
  "Emitted with Energy Capture CO2e",
  "Emitted with Energy Capture Change CO2e",
  "Emitted without Energy Capture CO2e",
  "Emitted without Energy Capture Change CO2e",
  "Reused Products in Use MgC",
  "Reused Products in Use Change MgC",
  "New Products in Use MgC",
  "New Products in Use Change MgC",
  "SWDS MgC",
  "SWDS Change MgC",
  "Present MgC",
  "Present Change MgC",
];
header_dict["total_yearly_dispositions2"] = [
  // "Year",
  // "SWDS Present Change MgC",
  // "Emitted with Energy Capture CO2e",
  // "Emitted with Energy Capture Change CO2e",
  // "Emitted without Energy Capture CO2e",
  // "Emitted without Energy Capture Change CO2e",
  // "Products in Use Change Mgc",
  // "SWDS MgC",
  // "SWDS Change MgC",
  // "Total Remaining MgC",
  // "Total Change MgC",
  // "Present Change MgC"

  "Year",
  "Emitted with Energy Capture CO2e",
  "Emitted with Energy Capture Change CO2e",
  "Emitted without Energy Capture CO2e",
  "Emitted without Energy Capture Change CO2e",
  // "Reused Products in Use MgC",
  // "Reused Products in Use Change MgC",
  "Products in Use MgC",
  "Products in Use Change MgC",
  "SWDS MgC",
  "SWDS Change MgC",
  "Present MgC",
  "Present Change MgC",
];
header_dict["total_selected_dispositions"] = [
  "Year",
  "Emitted with Energy Capture CO2e",
  "Emitted with Energy Capture Change CO2e",
  "Emitted without Energy Capture CO2e",
  "Emitted without Energy Capture Change CO2e",
  "Reused Products in Use MgC",
  "Reused Products in Use Change MgC",
  "New Products in Use MgC",
  "New Products in Use Change MgC",
  "SWDS MgC",
  "SWDS Change MgC",
  "Present MgC",
  "Present Change MgC",
];
header_dict["total_selected_dispositions2"] = [
  "Year",
  "Emitted with Energy Capture CO2e",
  "Emitted with Energy Capture Change CO2e",
  "Emitted without Energy Capture CO2e",
  "Emitted without Energy Capture Change CO2e",
  // "Reused Products in Use MgC",
  // "Reused Products in Use Change MgC",
  "Products in Use MgC",
  "Products in Use Change MgC",
  "SWDS MgC",
  "SWDS Change MgC",
  "Present MgC",
  "Present Change MgC",
];
header_dict["all_final_results_table"] = [
  "Year",
  "New Products in Use CO2e",
  "Reused Products in Use CO2e",
  "SWDS Present CO2e",
  "Emitted with Energy Capture CO2e",
  "Emitted without Energy Capture CO2e",
  "Sum CO2e"

]
header_dict["all_final_results_table2"] = [
  "Year",
  "New Products in Use CO2e",
  "SWDS Present C02e",
  "Emitted with Energy Capture CO2e",
  "Emitted without Energy Capture CO2e",
  "Sum CO2e"
]

header_dict["all_final_results_hidden_table"] = [
  "Year",
  "New Products in Use CO2e",
  "Reused Products in Use CO2e",
  "SWDS Present CO2e",
  "Emitted with Energy Capture CO2e",
  "Emitted without Energy Capture CO2e",
  "Sum CO2e"

]
header_dict["all_final_results_hidden_table2"] = [
  "Year",
  "New Products in Use CO2e",
  "SWDS Present C02e",
  "Emitted with Energy Capture CO2e",
  "Emitted without Energy Capture CO2e",
  "Sum CO2e"
]

output.initialize = function (input_json, bucket, file_name, is_single, scenario_json) {
  data_bucket = bucket;
  data_file_name = file_name;
  let data_json = input_json;
  data_json = data_json.replace(/\n/g, "\\n");
  let final_json = JSON.parse(data_json);
  scenario_json = scenario_json.replace(/\n/g, "\\n");
  deliver_scenario_json = scenario_json;
  // scenario_json = scenario_json.replace("\\","")
  // user_scenario_json = JSON.parse(scenario_json)

  display_user_data(scenario_json);

  
  const data = d3.csvParse(final_json.annual_harvest_and_timber_product_output);
  harvestminDateYear = data[0].Year;
  harvestmaxDateYear = data[data.length - 1].Year;
  
  if (is_single == "true") {
    $("#singleYearBtn").attr("checked", "true");
    $("#yearInput-1").show("fast");
    $(".graph.non-active.annual_harvest_and_timber_product_output").css(
      "display",
      "none"
    );
    needs_single_year_title = true
  }
  data_dict["annual_harvest_and_timber_product_output"] = [
    final_json.annual_harvest_and_timber_product_output,
    "Annual Harvest and Timber Products",
    "multiline",
    "Hundred Cubic Feet (CCF)",
  ];
  data_dict["annual_net_change_carbon_stocks"] = [
    final_json.annual_net_change_carbon_stocks,
    "Annual Net Change Carbon Stocks",
    "bar",
    "Metric Tons CO<sub>2</sub>e",
  ];
  data_dict["all_results_final"] = [
    final_json.big_four,
    "Final Results",
    "stack",
    "Metric Tons CO<sub>2</sub>e",
  ];
  // data_dict["annual_harvests_output"] = [final_json.harvest_data,"Annual Total Harvest","line"]
  data_dict["burned_with_energy_capture_emissions"] = [
    final_json.burned_w_energy_capture_emit,
    "Total Carbon Burned With Energy Capture",
    "line",
    "Metric Tons CO<sub>2</sub>e",
  ];
  data_dict["burned_without_energy_capture_emissions"] = [
    final_json.burned_wo_energy_capture_emit,
    "Total Carbon Burned Without Energy Capture",
    "line",
    "Metric Tons CO<sub>2</sub>e",
  ];

  data_dict["end_use"] = [
    final_json.total_end_use_products,
    "Total End Use Products",
    "line",
    "Metric Tons CO<sub>2</sub>e",
  ];
  data_dict["swds"] = [
    final_json.swds,
    "Total SWDS",
    "line",
    "Metric Tons CO<sub>2</sub>e",
  ];
  data_dict["total_composted_carbon_emitted"] = [
    final_json.total_composted_carbon_emitted,
    "Total Carbon in Compost Emitted",
    "line",
    "Metric Tons CO<sub>2</sub>e",
  ];
  data_dict["total_cumulative_carbon_stocks"] = [
    final_json.total_cumulative_carbon_stocks,
    "Total Cumulative Carbon Stocks",
    "stack",
    "Metric Tons CO<sub>2</sub>e",
  ];
  data_dict["total_dumps_carbon"] = [
    final_json.total_dumps_carbon,
    "Total Carbon in Dumps",
    "line",
    "Metric Tons CO<sub>2</sub>e",
  ];
  data_dict["total_dumps_carbon_emitted"] = [
    final_json.total_dumps_carbon_emitted,
    "Total Carbon in Dumps Emitted",
    "line",
    "Metric Tons CO<sub>2</sub>e",
  ];
  data_dict["total_fuelwood_carbon_emitted"] = [
    final_json.total_fuelwood_carbon_emitted,
    "Total Emitted Fuelwood Carbon",
    "line",
    "Metric Tons CO<sub>2</sub>e",
  ];
  data_dict["total_in_use"] = [
    final_json.total_in_use,
    "Total Carbon in Use",
    "line",
    "Metric Tons CO<sub>2</sub>e",
  ];
  data_dict["total_landfills_carbon"] = [
    final_json.total_landfills_carbon,
    "Total Landfills Carbon",
    "line",
    "Metric Tons CO<sub>2</sub>e",
  ];
  data_dict["total_landfills_carbon_emitted"] = [
    final_json.total_landfills_carbon_emitted,
    "Total Landfills Carbon Emitted",
    "line",
    "Metric Tons CO<sub>2</sub>e",
  ];
  data_dict["total_solid_carbon_dispositions"] = [
    final_json.carbon_present_distinct_swds,
    "Total Cumulative Solid Carbon Dispositions",
    "stack",
    "Metric Tons CO<sub>2</sub>e",
  ];
  data_dict["total_solid_carbon_dispositions2"] = [
    final_json.carbon_present_distinct_swds,
    "Total Cumulative Solid Carbon Dispositions",
    "stack",
    "Metric Tons CO<sub>2</sub>e",
  ];
  data_dict["swds_emissions"] = [
    final_json.carbon_emitted_distinct_swds,
    "Total SWDS Emissions",
    "stack",
    "Metric Tons CO<sub>2</sub>e",
  ];
  data_dict["total_emissions_dispositions"] = [
    final_json.emitted_all,
    "Total Cumulative Emissions",
    "stack",
    "Metric Tons CO<sub>2</sub>e",
  ];
  data_dict["total_emissions_dispositions2"] = [
    final_json.emitted_all,
    "Total Cumulative Emissions",
    "stack",
    "Metric Tons CO<sub>2</sub>e",
  ];

  //Data_dict for Tables
  data_dict["annual_timber_harvest_table"] = [
    final_json.annual_harvest_and_timber_product_output,
    "Annual Timber Product Output",
    "table",
    "",
  ];
  data_dict["total_yearly_net_change"] = [
    final_json.total_yearly_net_change,
    "Total Yearly Net Change",
    "table",
    "",
  ];
  data_dict["total_selected_net_change"] = [
    final_json.total_selected_net_change,
    "Total Selected Net Change",
    "table",
    "",
  ];
  data_dict["total_yearly_dispositions"] = [
    final_json.total_yearly_dispositions,
    "Total Yearly Dispositions",
    "table",
    "",
  ];
  data_dict["total_selected_dispositions"] = [
    final_json.total_selected_dispositions,
    "Total Selected Dispositions",
    "table",
    "",
  ];

  //Data Dict for hidden graphs (unique identifiers)
  data_dict["all_results_final_hidden"] = [
    final_json.big_four,
    "Final Results",
    "stack",
    "Metric Tons CO<sub>2</sub>e",
  ];
  data_dict["total_solid_carbon_dispositions_hidden"] = [
    final_json.carbon_present_distinct_swds,
    "Total Cumulative Solid Carbon Dispositions",
    "stack",
    "Metric Tons CO<sub>2</sub>e",
  ];
  data_dict["total_emissions_dispositions_hidden"] = [
    final_json.emitted_all,
    "Total Cumulative Emissions",
    "stack",
    "Metric Tons CO<sub>2</sub>e",
  ];
  data_dict["annual_net_change_carbon_stocks_hidden"] = [
    final_json.annual_net_change_carbon_stocks,
    "Annual Net Change Carbon Stocks",
    "bar",
    "Metric Tons CO<sub>2</sub>e",
  ];
  data_dict["annual_harvest_and_timber_product_output_hidden"] = [
    final_json.annual_harvest_and_timber_product_output,
    "Annual Harvest and Timber Products",
    "multiline",
    "Hundred Cubic Feet (CCF)",
  ];
  data_dict["burned_with_energy_capture_emissions_hidden"] = [
    final_json.burned_w_energy_capture_emit,
    "Total Carbon Burned With Energy Capture",
    "line",
    "Metric Tons CO<sub>2</sub>e",
  ];
  data_dict["burned_without_energy_capture_emissions_hidden"] = [
    final_json.burned_wo_energy_capture_emit,
    "Total Carbon Burned Without Energy Capture",
    "line",
    "Metric Tons CO<sub>2</sub>e",
  ];
  data_dict["swds_emissions_hidden"] = [
    final_json.carbon_emitted_distinct_swds,
    "Total Cumulative Emissions Dispositions",
    "stack",
    "Metric Tons CO<sub>2</sub>e",
  ];

  //Data Dict for table tab
  data_dict["all_final_results_table"] = [
    final_json.big_four,
    "Final Results",
    "table",
    "",
  ];
  data_dict["all_final_results_hidden_table"] = [
    final_json.big_four,
    "Final Results",
    "table",
    "",
  ];
};



$("#defaultOpen").click(function (e) {
  let active_ids = [];
  for (const element of $("#cumulativeResultsContent").children()) {
   if (element.nodeName == "FIGURE") {
      active_ids.push(
        element.children[0].classList[
        element.children[0].classList
          .length - 1
        ]
     );
    }
  }
  for (const element of active_ids) {
      generate_graph(
        data_dict[element][0],
        element,
        "active",
        data_dict[element][1],
        data_dict[element][2],
        captions_dict[element]
    ); 
  }
});
$("#solidCarbon").click(function (e) {
  let active_ids = [];
  for (const element of $("#solidCarbonContent").children()) {
    console.log(element)
    if (element.nodeName == "FIGURE") {
      active_ids.push(
        element.children[0].classList[
        element.children[0].classList
          .length - 1
        ]
      );
    }
  }
  for (const element of active_ids) {
      generate_graph(
        data_dict[element][0],
        element,
        "active",
        data_dict[element][1],
        data_dict[element][2],
        captions_dict[element]
      );
    }
});

$("#emissions").click(function (e) {
  //emissionsContent
  let active_ids = [];
  for (const element of $("#emissionsContent").children()) {
    if (element.nodeName == "FIGURE") {
      active_ids.push(
        element.children[0].classList[
        element.children[0].classList
          .length - 1
        ]
      );}
  }
  for (const element of active_ids) {
      generate_graph(
        data_dict[element][0],
        element,
        "active",
        data_dict[element][1],
        data_dict[element][2],
        captions_dict[element]
      );
    }
});

// $("#reused").click(function (e) {
//   let active_id =
//     $("#reusedContent").children()[0].classList[
//       $("#reusedContent").children()[0].classList.length - 1
//     ];
//   let inactive_ids = [];
//   for (const element of $("#reusedContent").children()[1].children) {
//     inactive_ids.push(
//       element.classList[
//         element.classList.length - 1
//       ]
//     );
//   }
//   generate_graph(
//     data_dict[active_id][0],
//     active_id,
//     "active",
//     data_dict[active_id][1],
//     data_dict[active_id][2],
//     captions_dict[active_id]
//   );
//   for (const element of inactive_ids) {
//     generate_graph(
//       data_dict[element][0],
//       element,
//       "inactive",
//       data_dict[element][1],
//       data_dict[element][2],
//     );
//   }
// });

$("#table").click(function (e) {
 let active_id =
    $("#tableContent").children()[0].classList[
    $("#tableContent").children()[0].classList.length - 1
    ];
 

  generate_table(
    data_dict[active_id][0],
    active_id,
    data_dict[active_id][1],
    true
  )
});


// Keydown event listener
// $("#defaultOpen").keydown(function (e) {
//   if (e.which === 32 || e.which === 13) {
//     let active_id = $("#cumulativeResultsContent").children()[0].classList[
//       $("#cumulativeResultsContent").children()[0].classList.length - 1
//     ];
    
//     let inactive_ids = [];
//     for (const element of $("#cumulativeResultsContent").children()[1].children) {
//       inactive_ids.push(
//         element.classList[
//           element.classList
//             .length - 1
//         ]
//       );
//     }
//     generate_graph(
//       data_dict[active_id][0],
//       active_id,
//       "active",
//       data_dict[active_id][1],
//       data_dict[active_id][2],
//       captions_dict[active_id]
//     );
//     for (const element of inactive_ids) {
//       generate_graph(
//         data_dict[element][0],
//         element,
//         "inactive",
//         data_dict[element][1],
//         data_dict[element][2]
//       );
//     }
//   }
// });

// $("#solidCarbon").keydown(function (e) {
//   if (e.which === 32 || e.which === 13) {
//     let active_id = $("#solidCarbonContent").children()[0].classList[
//       $("#solidCarbonContent").children()[0].classList.length - 1
//     ];
    
//     let inactive_ids = [];
//     for (const element of $("#solidCarbonContent").children()[1].children) {
//       inactive_ids.push(
//         element.classList[
//           element.classList.length -
//             1
//         ]
//       );
//     }
//     generate_graph(
//       data_dict[active_id][0],
//       active_id,
//       "active",
//       data_dict[active_id][1],
//       data_dict[active_id][2],
//       captions_dict[active_id]
//     );
//     for (const element of inactive_ids) {
//       generate_graph(
//         data_dict[element][0],
//         element,
//         "inactive",
//         data_dict[element][1],
//         data_dict[element][2],
//       );
//     }
//   }
// });

// $("#emissions").keydown(function (e) {
//   if (e.which === 32 || e.which === 13) {
//     let active_id =
//       $("#emissionsContent").children()[0].classList[
//         $("#emissionsContent").children()[0].classList.length - 1
//       ];
    
//     let inactive_ids = [];
//     for (const element of $("#emissionsContent").children()[1].children) {
//       inactive_ids.push(
//         element.classList[
//           element.classList.length - 1
//         ]
//       );
//     }
//     generate_graph(
//       data_dict[active_id][0],
//       active_id,
//       "active",
//       data_dict[active_id][1],
//       data_dict[active_id][2],
//       captions_dict[active_id]
//     );
//     for (const element of inactive_ids) {
//       generate_graph(
//         data_dict[element][0],
//         element,
//         "inactive",
//         data_dict[element][1],
//         data_dict[element][2],
//       );
//     }
//   }
// });

// $("#reused").keydown(function (e) {
//   if (e.which === 32 || e.which === 13) {
//     let active_id =
//       $("#reusedContent").children()[0].classList[
//         $("#reusedContent").children()[0].classList.length - 1
//       ];
    
//     let inactive_ids = [];
//     for (const element of $("#reusedContent").children()[1].children) {
//       inactive_ids.push(
//         element.classList[
//           element.classList.length - 1
//         ]
//       );
//     }
//     generate_graph(
//       data_dict[active_id][0],
//       active_id,
//       "active",
//       data_dict[active_id][1],
//       data_dict[active_id][2],
//       captions_dict[active_id]
//     );
//     for (const element of inactive_ids) {
//       generate_graph(
//         data_dict[element][0],
//         element,
//         "inactive",
//         data_dict[element][1],
//         data_dict[element][2],
//       );
//     }
//   }
// });


function generate_graph(
  json_data,
  graph_class,
  is_active,
  title,
  graph_type,
  caption
) {
  let stackedData = [];
  
  $("." + graph_class).html("");
  let tester
  console.log(graph_class)
  if (graph_type == "line") {
    if (graph_class.includes("hidden")) { 
      tester = document.getElementsByClassName(
        "hidden " + graph_class
      )[0];
    }
    else {
      tester = document.getElementsByClassName(
        "active-graph " + graph_class
      )[0];
    }
    
   
    const data = d3.csvParse(json_data);

    let minDateYear = data[0].year;
    let maxDateYear = data[data.length - 1].year;
    caption[0].text = caption[0].text.replace("[minimum year]", minDateYear);
    caption[0].text = caption[0].text.replace("[maximum year]", maxDateYear);
    tester.nextElementSibling.innerHTML = caption[0].text;

    let year_array = [];
    let value_array = [];

    for (let i in data) {
      year_array.push(data[i][data.columns[0]]);
      value_array.push(data[i][data.columns[1]]);
    }

    let trace1 = {
      x: year_array,
      y: value_array,
      name: data_dict[graph_class][1],
      type: "scatter",
    };

    let layout = {
      title: data_dict[graph_class][1],
      xaxis: { title: "Year<br><br>" },
      yaxis: { title: data_dict[graph_class][3] },
      automargin: true,
      height: 500,
      margin: { l: 70, r: 10, b: 50, t: 100, pad: 4 },
      

    };

    let config = {
      responsive: true,
      autosize: true,
    }

    let stackedData = [trace1];

   
    
    Plotly.newPlot(tester, stackedData, layout, config);
  


    // if (window.innerWidth > 1200) {
    //   console.log("window width is greater than 1200")
    //   var layout_update = {
    //     height: 700,
    //   }
    //   Plotly.update(tester, stackedData, layout_update, config);
  
    // } else if (window.innerWidth <= 1200) {
    //   console.log("window width is less than 1200")
    //   var layout_update = {
    //     height: 300,
    //   }
    //   Plotly.update(tester, stackedData, layout_update, config);
    // }

  

  } else if (graph_type == "multiline") {
    console.log("graph type is active multiline");
    if (graph_class.includes("hidden")) { 
      tester = document.getElementsByClassName(
        "hidden " + graph_class
      )[0];
    }
    else {
      tester = document.getElementsByClassName(
        "active-graph " + graph_class
      )[0];
    }
    const data = d3.csvParse(json_data, function (d) {
      return {
        year: d[Object.keys(d)[0]],
        value1: d[Object.keys(d)[1]],
        value2: d[Object.keys(d)[2]],
      };
    });
    

    let minDateYear = data[0].year;
    let maxDateYear = data[data.length - 1].year;
    caption[0].text = caption[0].text.replace("[minimum year]", minDateYear);
    caption[0].text = caption[0].text.replace("[maximum year]", maxDateYear);
    tester.nextElementSibling.innerHTML = caption[0].text;

    let year_array = [];
    let value1_array = [];
    let value2_array = [];
    for (let i in data) {
      year_array.push(data[i].year);
      value1_array.push(data[i].value1);
      value2_array.push(data[i].value2);
    }

    let trace1 = {
      x: year_array,
      y: value1_array,
      name: "Annual Harvest",
      type: "scatter",
    };

    let trace2 = {
      x: year_array,
      y: value2_array,
      yaxis: "y2",
      name: "Annual Timber Harvest",
      type: "scatter",
    };

    let layout = {
      title: "Annual Harvest and Timber Product Outputs",
      xaxis: { title: "Year<br><br>" },
      yaxis: { title: "Hundred Cubic Feet (CCF)" },
      yaxis2: {
        title: "Metric Tons CO<sub>2</sub>e",
        titlefont: { color: "rgb(148, 103, 189)" },
        tickfont: { color: "rgb(148, 103, 189)" },
        overlaying: "y",
        side: "right",
      },
      margin: { l: 60, r: 50, b: 50, t: 250 },
      height: 600,
      legend: {
        yanchor: "top",
        y: 1.3,
        xanchor: "left",
        x: 0.01,
      }
    };
    let config = {
      responsive: true,
      autosize: true,
    };
    
    
    let stackedData = [trace1, trace2];
    Plotly.newPlot(tester, stackedData, layout, config);
    
  } else if (graph_type == "stack") {
    if (graph_class.includes("hidden")) { 
      tester = document.getElementsByClassName(
        "hidden " + graph_class
      )[0];
    }
    else {
      tester = document.getElementsByClassName(
        "active-graph " + graph_class
      )[0];
    }
    const data = d3.csvParse(json_data);
    stackedData = [];
    let year_data = [];
    let emissions_present = false;
    let solid_present = false;
    
    let minDateYear = data[0].Year;
    let maxDateYear = data[data.length - 1].Year;
    caption[0].text = caption[0].text.replace("[minimum year]", minDateYear);
    caption[0].text = caption[0].text.replace("[maximum year]", maxDateYear);
    tester.nextElementSibling.innerHTML = caption[0].text;

    for (let i in data.columns) {
      if (data.columns[i].includes("co2e")) {
        emissions_present = true;
      }
      if (
        !data.columns[i].includes("co2e") &&
        !data.columns[i].includes("Year")
      ) {
        solid_present = true;
      }
    }
    for (let i in data.columns) {
      let column = data.columns[i];
      if (i == 0) {
        for (let j in data) {
          year_data.push(data[j][column]);
        }
      } else {
        let temp = [];
        for (let j in data) {
          temp.push(data[j][column]);
        }
        
        let colorHex = "#333";
        let y_name = ""
        let temp_trace = ""
        
        if (column == "products_in_use") {
          y_name = "Products in Use";
          colorHex = colors["darkBlue"];
        }
        if (column == "products_in_use_mgc") {
          y_name = "Products in Use";
          colorHex = colors["darkBlue"];
        }
        if (column == "products_in_use_present_co2e") {
          y_name = "Products in Use";
          colorHex = colors["darkBlue"];
        }
        if (column == "SWDS") {
          y_name = "SWDS";
          colorHex = colors["green"];
        }
        if (column == "SWDS_mgc") {
          y_name = "SWDS";
          colorHex = colors["green"];
        }
        if (column == "SWDS_present_co2e") {
          y_name = "SWDS";
          colorHex = colors["green"];
        }
        if (column == "emitted_w_energy_capture_emitted_co2e") {
          y_name = "Emitted with Energy Capture";
          colorHex = colors["lightRed"];
        }
        if (column == "emitted_w_energy_capture") {
          y_name = "Emitted with Energy Capture";
          colorHex = colors["lightRed"];
        }
        if (column == "emitted_wo_energy_capture") {
          y_name = "Emitted without Energy Capture";
          colorHex = colors["darkRed"];
        }
        if (column == "emitted_wo_energy_capture_emitted_co2e") {
          y_name = "Emitted without Energy Capture";
          colorHex = colors["darkRed"];
        }
        if (column == "Fuel_emitted_co2e") {
          y_name = "Fuelwood Emissions";
          colorHex = colors["fuelwood_emissions"];
        }
        if (column == "Composted_emitted_co2e") {
          y_name = "Compost Emissions";
          colorHex = colors["compost_emissions"];
        }
        if (column == "Dumps_emitted_mgc") {
          y_name = "Dump Emissions";
          colorHex = colors["dump_emissions"];
        }
        if (column == "Dumps_emitted_co2e") {
          y_name = "Dump Emissions";
          colorHex = colors["dump_emissions"];
        }
        if (column == "Landfills_emitted_co2e") {
          y_name = "Landfill Emissions";
          colorHex = colors["landfill_emissions"];
        }
        if (column == "Dumps_present_mgc") {
          y_name = "Carbon in Dumps";
          colorHex = colors["dump_emissions"];
        }
        if (column == "Landfills_present_mgc") {
          y_name = "Carbon in Landfills";
          colorHex = colors["landfill_emissions"];
        }
        if (column == "new_products_in_use") {
          y_name = "Products in Use, original";
          colorHex = colors["darkBlue"];
        }
        if (column == "reused_products_in_use") {
          y_name = "Products in Use, recycled  ";
          colorHex = colors["lightBlue"];
        }
        if (column == "new_products_in_use_co2e") {
          y_name = "Products in Use, original";
          colorHex = colors["darkBlue"];
        }
        if (column == "reused_products_in_use_co2e") {
          y_name = "Products in Use, recycled  ";
          colorHex = colors["lightBlue"];
        }
        if (column == "new_products_in_use_present_co2e") {
          y_name = "Products in Use, original";
          colorHex = colors["darkBlue"];
        }
        if (column == "reused_products_in_use_present_co2e") {
          y_name = "Products in Use, recycled  ";
          colorHex = colors["lightBlue"];
        }
        if (column == "new_products_in_use_mgc") {
          y_name = "Products in Use, original";
          colorHex = colors["darkBlue"];
        }
        if (column == "reused_products_in_use_mgc") {
          y_name = "Products in Use, recycled  ";
          colorHex = colors["lightBlue"];
        }
        if (emissions_present && !solid_present) {
          temp_trace = {
            x: year_data,
            y: temp,
            name: y_name,
            stackgroup: "one",
            line: { color: colorHex }
          };
        }
        if (emissions_present && solid_present) {
          if (column.includes("emit")) {
            temp_trace = {
              x: year_data,
              y: temp,
              yaxis: "y2",
              name: y_name,
              stackgroup: "one",
              line: { color: colorHex }
            };
          } else {
            temp_trace = {
              x: year_data,
              y: temp,
              name: y_name,
              stackgroup: "one",
              line: { color: colorHex }
            };
          }
        }
        if (!emissions_present && solid_present) {
          temp_trace = {
            x: year_data,
            y: temp,
            name: y_name,
            stackgroup: "one",
            line: { color: colorHex }
          };
        }
        stackedData.push(temp_trace);
      }
    }

    let y_buffer = 0.0
    let layout = ""
    if (emissions_present && !solid_present) {
      if (title == "Final Results") {
        y_buffer = -0.45
      }
      else if (title == "Total SWDS Emissions") {
        y_buffer = -0.45
      }
      else {
        y_buffer = -0.6
      }
      layout = {
        title: title,
        xaxis: { title: "Year<br><br>" },
        yaxis: { title: "Metric Tons CO<sub>2</sub>e" },
        margin: { l: 60, r: 0, b: 50, t: 205 },
        height: 600,
        legend: {
          yanchor: "top",
          y: 1.2,
          xanchor: "left",
          x: 0.01
        }
      
      };
    }
    if (emissions_present && solid_present) {
      layout = {
        title: title,
        autosize: true,
        xaxis: { title: "Year<br><br>:" },
        yaxis: { title: "Metric Tons CO<sub>2</sub>e" },
        yaxis2: {
          title: "Metric Tons CO<sub>2</sub>e",
          // titlefont: {color: 'rgb(148, 103, 189)'},
          // tickfont: {color: 'rgb(148, 103, 189)'},
          overlaying: "y",
          side: "right",
        },
        margin: { l: 60, r: 0, b: 50, t: 205 },
        height: 600,

       
        legend: {
          yanchor: "top",
          y: 1.2,
          xanchor: "left",
          x: 0.01
        }
      };
    }
    if (!emissions_present && solid_present) {
      if (title == "Total Cumulative Solid Carbon Dispositions") {
        y_buffer = -0.5
      }
      else {
        y_buffer = -0.4
      }
      layout = {
        title: title,
        xaxis: { title: "Year<br><br>" },
        yaxis: { title: "Metric Tons Carbon" },
        margin: { l: 60, r: 0, b: 50, t: 205 },
        height: 600,
        legend: {
          yanchor: "top",
          y: 1.2,
          xanchor: "left",
          x: 0.01
        }
      };
    }
    let config = {
      responsive: true,
      autosize: true,
    };

    Plotly.newPlot(tester, stackedData, layout, config);
  }
  else {
    if (graph_class.includes("hidden")) { 
      tester = document.getElementsByClassName(
        "hidden " + graph_class
      )[0];
    }
    else {
      tester = document.getElementsByClassName(
        "active-graph " + graph_class
      )[0];
    }
    const data = d3.csvParse(json_data, function (d) {
      return {
        year: d[Object.keys(d)[0]],
        products_in_use_change: d[Object.keys(d)[1]],
        SWDS_change: d[Object.keys(d)[2]],
      };
    });
    let minDateYear = data[0].year;
    let maxDateYear = data[data.length - 1].year;
    console.log(caption)
    caption[0].text = caption[0].text.replace("[minimum year]", minDateYear);
    caption[0].text = caption[0].text.replace("[maximum year]", maxDateYear);
    tester.nextElementSibling.innerHTML = caption[0].text;
      
    let year_array = [];
    let prod_array = [];
    let swds_array = [];
    let net_change_array = [];
      
    for (let i in data) {
      year_array.push(data[i].year);
      prod_array.push(data[i].products_in_use_change);
      swds_array.push(data[i].SWDS_change);
      
      let temp1 = parseInt(data[i].products_in_use_change);
      let temp2 = parseInt(data[i].SWDS_change);
      let temp3 = temp1 + temp2;
      
      net_change_array.push(temp3);
    }
            
    year_array = year_array.slice(0, -2);
    prod_array = prod_array.slice(0, -2);
    swds_array = swds_array.slice(0, -2);
    net_change_array = net_change_array.slice(0, -2);
      
    let trace1 = {
      x: year_array,
      y: prod_array,
      name: "Change in Products in Use",
      marker: { color: colors["darkBlue"] },
      type: "bar",
    };
      
    let trace2 = {
      x: year_array,
      y: swds_array,
      name: "Change in SWDS",
      marker: { color: colors["green"] },
      type: "bar",
    };
      
    let trace3 = {
      x: year_array,
      y: net_change_array,
      name: "Net Change",
      line: { color: "black" },
      type: "scatter",
    };
      
    stackedData = [trace1, trace2, trace3];
      
    let layout = {
      barmode: "relative",
      xaxis: { title: "Year<br><br>" },
      yaxis: { title: "Metric Tons CO<sub>2</sub>e" },
      title: "Annual Net Change Carbon Stocks", 
      margin: { l: 60, r: 0, b: 50, t: 220 },
      height: 600,
      legend: {
        yanchor: "top",
        y: 1.2,
        xanchor: "left",
        x: 0.01
      }
    };
    let config = {
      responsive: true,
      autosize: true,
    };

    Plotly.newPlot(tester, stackedData, layout, config);
  }
  

};

function generate_table(json_data, table_class, title, is_big_four = false) {
  let tester
  if (is_big_four) {
    tester = document.getElementsByClassName(table_class)[0];
  } else {
    tester = document.getElementsByClassName("hidden " + table_class)[0];
  }
  
  const data = d3.csvParse(json_data);
  try{
    process_data(data);
  }
  catch{
    console.log("error in table generation")
  }
  function process_data(rows) {
    function unpack(rows, key) {
      return rows.map(function (row) {
        return row[key];
      });
    }

    let headerNames = Object.keys(rows[0]);
    if (is_big_four) {
      headerNames.push("Sum CO2e")
    }


    let imageWidth = 0;


    if (headerNames.length <= 5) {
      imageWidth = 1225; // pdf exports at letter mm size, 2551px will give it 144ppi 'resolution'
    } else {
      imageWidth = 1582;
    }

    let headerColor = "grey";

    let headerValues = [];
    let cellValues = [];
    let cellValue
    let headerValue
    let rolling_sum = []
    for (let i = 0; i < headerNames.length; i++) {
      headerValue = [headerNames[i]];
      headerValues[i] = headerValue;
      cellValue = unpack(rows, headerNames[i]);

      if(is_big_four){
        console.log("in big four logic loop")
        if (i >= 1 && i != headerNames.length-1) {
          let temp = [];
          let temp2=[]
          for (const element of cellValue) {
              if (is_big_four) {
                temp.push(parseInt(element).toLocaleString());
                temp2.push(parseInt(element))
            }
              else {
                temp.push(parseFloat(element).toFixed(2).toLocaleString());
                temp2.push(parseFloat(element).toFixed(2))
              }
            }
            rolling_sum.push(temp2)
            cellValues[i] = temp;
          }
  
        else if(i == headerNames.length-1){
            let temp = [];
            if (is_big_four) {
              for (let j = 0; j < rolling_sum[0].length; j++) {
                let result = 0
                for (const element of rolling_sum) {
                  result += element[j]
                }
              temp.push(result.toLocaleString());
            }
          cellValues[i] = temp;
            }
          }
        else {
          cellValues[i] = cellValue;
        }
      }
      else{
        if (i >= 1) {
          let temp = [];
          let temp2=[]
          for (const element of cellValue) {
              if (is_big_four) {
                temp.push(parseInt(element).toLocaleString());
                temp2.push(parseInt(element))
            }
              else {
                temp.push(parseFloat(element).toFixed(2).toLocaleString());
                temp2.push(parseFloat(element).toFixed(2))
              }
            }
            rolling_sum.push(temp2)
            cellValues[i] = temp;
          }
  
        else if(i == headerNames.length-1){
            let temp = [];
            if (is_big_four) {
              for (let j = 0; j < rolling_sum[0].length; j++) {
                let result = 0
                for (const element of rolling_sum) {
                  result += element[j]
                }
              temp.push(result.toLocaleString());
            }
          cellValues[i] = temp;
            }
          }
        else {
          cellValues[i] = cellValue;
        }
      }
      
      
    }
    // clean date
    for (let i = 0; i < cellValues[1].length; i++) {
      let dateValue = cellValues[1][i].split(" ")[0];
      cellValues[1][i] = dateValue;
    }
    let headers_values = ""
    if (needs_single_year_title) {
      if($("#singleYear").val()<1970 && table_class != "annual_timber_harvest_table" && table_class != "total_yearly_net_change"){
        headers_values = header_dict[table_class+"2"]
      }
      else{
        headers_values = header_dict[table_class]
      }
    }
    else{
      headers_values = header_dict[table_class]
    }
    
    let data_layout = [
      {
        type: "table",
        columnwidth: [25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25],
        columnorder: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
        header: {
          values: headers_values,
          line: { width: 1, color: "rgb(50, 50, 50)" },
          fill: { color: headerColor },
          font: { family: "Open Sans", size: 14, color: "white" },
        },
        cells: {
          values: cellValues,
          height: 25,
          align: ["center", "center"],
          line: { color: "gray", width: 1 },
          // fill: { color: "white" },
          font: { family: "Open Sans", size: 12, color: ["black"] },
        },
      },
    ];
    let layout = {
      title: title,
      height: (cellValues[0].length + 5) * 30 + 100,
      width: imageWidth,
    };

    let config = {
      responsive: true
    }

    Plotly.newPlot(tester, data_layout, layout, config);
  }
};



$("#allYearsBtn").click(function (e) {
 
  $("#yearfilter").attr(
    "href",
    "/output?p=" + data_bucket + "&q=" + data_file_name
  );
});

$("#singleYearBtn").click(function (e) {
  $("#yearfilter").attr(
    "href",
    "/output?p=" +
      data_bucket +
      "&q=" +
      data_file_name +
      "&y=" +
      $("#singleYear").val()
  );
});

$("#singleYear").on("change", function (e) {
  $("#yearfilter").attr(
    "href",
    "/output?p=" +
      data_bucket +
      "&q=" +
      data_file_name +
      "&y=" +
      $("#singleYear").val()
  );
});

$("#singleYear").on('keypress', function (e) {
  if (e.keyCode === 13) {
      e.preventDefault();
    document.getElementById('yearfilter').href = "/output?p=" +
    data_bucket +
    "&q=" +
    data_file_name +
      "&y=" +
      $("#singleYear").val();
      document.getElementById('yearfilter').click();
  };
});

$(document).ready(function () {
  $("#yearfilter").attr(
    "href",
    "/output?p=" + data_bucket + "&q=" + data_file_name
  );
  $("#singleYear").attr({
    min: harvestminDateYear,
    max: harvestmaxDateYear,
    value: harvestminDateYear,
  });

});

// Harvest Years Controls

$(function () {
  $("#blk-" + $("[name=harvestYears]:checked").val()).show();
  $("[name=harvestYears]").click(function () {
    $(".toHide").hide();
    $("#yearInput-" + $(this).val()).show("fast");
  });
});

d3.select("#dl-closed").on("click", function () {
  generate_table(
    data_dict["all_final_results_hidden_table"][0],
    "all_final_results_hidden_table",
    data_dict["all_final_results_hidden_table"][1],
    true
  );
  generate_table(
    data_dict["annual_timber_harvest_table"][0],
    "annual_timber_harvest_table",
    data_dict["annual_timber_harvest_table"][1]
  );
  generate_table(
    data_dict["total_yearly_net_change"][0],
    "total_yearly_net_change",
    data_dict["total_yearly_net_change"][1]
  );
  generate_table(
    data_dict["total_selected_net_change"][0],
    "total_selected_net_change",
    data_dict["total_selected_net_change"][1]
  );
  generate_table(
    data_dict["total_yearly_dispositions"][0],
    "total_yearly_dispositions",
    data_dict["total_yearly_dispositions"][1]
  );
  generate_table(
    data_dict["total_selected_dispositions"][0],
    "total_selected_dispositions",
    data_dict["total_selected_dispositions"][1]
  );

  generate_graph(
    data_dict["all_results_final_hidden"][0],
    "all_results_final_hidden",
    "active",
    data_dict["all_results_final_hidden"][1],
    data_dict["all_results_final_hidden"][2],
    captions_dict["all_results_final"]
  );
  generate_graph(
    data_dict["total_solid_carbon_dispositions_hidden"][0],
    "total_solid_carbon_dispositions_hidden",
    "active",
    data_dict["total_solid_carbon_dispositions_hidden"][1],
    data_dict["total_solid_carbon_dispositions_hidden"][2],
    captions_dict["total_solid_carbon_dispositions"]
  );
  generate_graph(
    data_dict["total_emissions_dispositions_hidden"][0],
    "total_emissions_dispositions_hidden",
    "active",
    data_dict["total_emissions_dispositions_hidden"][1],
    data_dict["total_emissions_dispositions_hidden"][2],
    captions_dict["total_emissions_dispositions"]
  );
  generate_graph(
    data_dict["annual_net_change_carbon_stocks_hidden"][0],
    "annual_net_change_carbon_stocks_hidden",
    "active",
    data_dict["annual_net_change_carbon_stocks_hidden"][1],
    data_dict["annual_net_change_carbon_stocks_hidden"][2],
    captions_dict["annual_net_change_carbon_stocks"]
  );
  generate_graph(
    data_dict["annual_harvest_and_timber_product_output_hidden"][0],
    "annual_harvest_and_timber_product_output_hidden",
    "active",
    data_dict["annual_harvest_and_timber_product_output_hidden"][1],
    data_dict["annual_harvest_and_timber_product_output_hidden"][2],
    captions_dict["annual_harvest_and_timber_product_output"]
  );
  generate_graph(
    data_dict["burned_with_energy_capture_emissions_hidden"][0],
    "burned_with_energy_capture_emissions_hidden",
    "active",
    data_dict["burned_with_energy_capture_emissions_hidden"][1],
    data_dict["burned_with_energy_capture_emissions_hidden"][2],
    captions_dict["burned_with_energy_capture_emissions"]
  );
  generate_graph(
    data_dict["burned_without_energy_capture_emissions_hidden"][0],
    "burned_without_energy_capture_emissions_hidden",
    "active",
    data_dict["burned_without_energy_capture_emissions_hidden"][1],
    data_dict["burned_without_energy_capture_emissions_hidden"][2],
    captions_dict["burned_without_energy_capture_emissions"]
  );
  generate_graph(
    data_dict["swds_emissions_hidden"][0],
    "swds_emissions_hidden",
    "active",
    data_dict["swds_emissions_hidden"][1],
    data_dict["swds_emissions_hidden"][2],
    captions_dict["swds_emissions"]
  );
});

// exports

window.jsPDF = window.jspdf.jsPDF;

let img_png = d3.select("#png-export");
let zip = new JSZip();

let big_count = 0;
let small_count = 0;
function export_tables() {
  //export plotly tables as pngs
  let title
  let tables = document.getElementsByClassName("graph hidden table");

  for (const element of tables) {
    if(needs_single_year_title){
      title = harvestminDateYear + "_" + element.classList[3]
    }
    else{
      title = element.classList[3]
    }
    big_count += 1;
    generate_tables(
      element,
      { format: "png" },
      title + ".pdf"
    );
  }
}

function savePDF(imageDataURL, file_name) {
  let image = new Image();
  image.onload = function () {
    let imgData = imageDataURL;
    let imageWidth = image.naturalWidth;
    let imageHeight = image.naturalHeight;
    let orientation = "";
    let imgWidth = 0;
    let pageHeight = 0;

    if (imageWidth >= 1582) {
      orientation = "landscape";
      imgWidth = 270;
      pageHeight = 213;
    } else {
      orientation = "portrait";
      imgWidth = 210;
      pageHeight = 279;
    }

    let imgHeight = (imageHeight * imgWidth) / imageWidth;
    let heightLeft = imgHeight;

    let pdf = new jsPDF({
      orientation: orientation,
      unit: "mm",
      format: "letter",
    });
    let position = 10; // give some top padding to first page

    pdf.addImage(imgData, "PNG", 0, position, imgWidth, imgHeight);
    heightLeft -= pageHeight;

    while (heightLeft >= 0) {
      position = heightLeft - imgHeight + 10; // top padding for other pages
      pdf.addPage();
      pdf.addImage(imgData, "PNG", 0, position, imgWidth, imgHeight);
      heightLeft -= pageHeight;
    }
    let blob = pdf.output("blob");
    zip.file(file_name, blob, { binary: true });
    small_count += 1;
    if (small_count == big_count) {
      if (document.getElementById("official_check").checked == true) {
        fetch('/set-official?p=' + data_bucket + '&q=' + data_file_name)
          .then(function (response) {
            return response.text();
          })
          .then(function (text) {
            console.log("GET response text:");
            console.log(text);
          });
      }
      zip.generateAsync({ type: "blob" }).then(function callback(content) {
        saveAs(content, data_file_name + ".zip");
      });
    }
  };
  image.src = imageDataURL;
}

async function generate_tables(div, options, file_name) {
  let url = await Plotly.toImage(div, options);
  savePDF(url, file_name);
}

function export_plots() {

  $(".dl-files")
    .children()
    .each(function () {
      let tempChk = $(this).children()[0];
      let title
      if (tempChk.checked) {
        if(needs_single_year_title){
          title = harvestminDateYear + "_" + tempChk.value.slice(0, -7)
        }
        else{
          title = tempChk.value.slice(0, -7)
        }
        let png_options = { format: "png", width: 1300, height: 700 };
        gen = generate_image(
          document.getElementsByClassName(tempChk.value)[0],
          png_options,
          title + ".png"
        );
      }
    });
}


async function generate_image(div, options, file_name) {
  let url = await Plotly.toImage(div, options);
  await zip.file(file_name, urlToPromise(url), { binary: true });
}

function export_csv() {
  let title
  for (let i in data_dict) {
    if (!i.includes("hidden") && !i.includes("2")) {
      if(needs_single_year_title){
        title = harvestminDateYear + "_" + i
      }
      else{
        title = i
      }
      zip.file(title + ".csv", data_dict[i][0], { binary: true });
    }
  }
}
//export csv files

function urlToPromise(url) {
  return new Promise(function (resolve, reject) {
    JSZipUtils.getBinaryContent(url, function (err, data) {
      if (err) {
        reject(err);
      } else {
        resolve(data);
      }
    });
  });
}

d3.select("#download").on("click", function () {
  export_plots();
  export_csv();
  export_tables();
  zip.file("user_input.json", deliver_scenario_json, { binary: true });

});


// function to display user data from scenario_json on output page

function display_user_data(temp_scenario_json) {
  temp_scenario_json = JSON.parse(temp_scenario_json.substring(1,temp_scenario_json.length-1))
  temp_scenario_json = temp_scenario_json.replace("\"\"","\"No\"")
  temp_scenario_json = JSON.parse(temp_scenario_json)
  jQuery.each(temp_scenario_json, function(i, val) {
    
    if(i == "region" ){
      $("#"+i).html(val.name)
    }
    else if(i == "inputs"){
      jQuery.each(val, function(j, j_val) {
        $("#"+j.slice(0,-4)).html(j_val)
      });
    }
    else if(i == "monte_carlo"){
      $("#"+i).html(val.iterations)
    }
    else{
      $("#"+i).html(val)
    }
  });

}
