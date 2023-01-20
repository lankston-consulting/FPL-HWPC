# HWPC-Web UI Mapping

## Step 1
Users deliver a file named **harvest_data.csv**. This step is paired with a radio selector to define the units of the harvest data, this selection is named **harvest_data_type**.

## Step 2
Users deliver a file named **timber_product_data.csv**.

## Step 3
Users have a choice, either they select a default region from the dropdown, and will deliver a file named **region**. This file will be used in the default data file **regions.csv** in order to define the primary product ratios of that region. 
If they use the second choice, they will define the name of their custom region, delivering the name in the file **region**. They will also deliver a file named **primary_product_data.csv**.

## Optional Steps
#### Step 4
Users deliver a file named **end_use_ratios.csv**.

#### Step 5
Users deliver a file named **end_use_half_lives.csv**.

#### Step 6 
Users deliver a file named **dispositions.csv**.

#### Step 7
Users deliver a file named **disposition_half_lives.csv**.

#### Step 8
Users deliver a file named **distribution_data.csv**.

#### Step 9
Users deliver a file named **burned_ratios.csv**.

#### Step 10
Users deliver a file named **mbf_to_ccf.csv**.

#### Step 11
Users deliver a file named **ccf_to_mgc.csv**.

### Step 12
Users input the loss_factor of the data, delivering it in the file **loss_factor**.

### Step 13
Users input the number of iterations desired for the Monte Carlo simulation, delivering it in the file **iterations**.
#### (optional-ish)
Users input their email to receive the finished Monte Carlo simulation data, delivering it in the file **email**.

### Step 14
Users input the name of the entire run to name the resulting zip folder, delivering it in the file **run_name**. 
