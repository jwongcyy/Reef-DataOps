import streamlit as st
import pandas as pd
import datetime
import os.path as path
import io
import os
import sys
from S3 import Storage
from helper import *

# Set root path for code modules
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

geo_codes={
    "United Arab Emirates" : "UAE",
    "Saudi Arabia" : "KSA",
    "Hong Kong" : "HKG",
    "Jordan" : "JOR",
    "Japan" : "JPN"
 }
root = path.abspath(path.join(__file__ ,"../../.."))

# Get Operational data
# clients=pd.read_csv(f'{root}/data/reefops/clients.csv')
# sites=pd.read_csv(f'{root}/data/reefops/sites.csv')
# agents=pd.read_csv(f'{root}/data/reefops/agents.csv')



s3_storage = Storage(name='archireef-hive')
client_storage_path = 'database/reef_ops/clients.csv'
# Load the data from aws s3 as binary format
loaded_clients_s3 = s3_storage.read_file(file_path=client_storage_path)
# Read the binary data
client_obj = io.BytesIO(loaded_clients_s3)
clients_df = pd.read_csv(client_obj)
cur_client_codes=clients_df.client_code
agent_storage_path = 'database/reef_ops/agents.csv'
# Load the data from aws s3 as binary format
loaded_agents_s3 = s3_storage.read_file(file_path=agent_storage_path)
# Read the binary data
agent_obj = io.BytesIO(loaded_agents_s3)
agents_df = pd.read_csv(agent_obj)


site_storage_path = 'database/reef_ops/sites.csv'
# Load the data from aws s3 as binary format
loaded_sites_s3 = s3_storage.read_file(file_path=site_storage_path)
# Read the binary data
site_obj = io.BytesIO(loaded_sites_s3)
sites_df = pd.read_csv(site_obj)

locality_path = 'database/reef_ops/locality.csv'
# Read the binary data
loaded_locality_s3=s3_storage.read_file(file_path=locality_path)
locality_obj = io.BytesIO(loaded_locality_s3)
locality_df = pd.read_csv(locality_obj)
locality_names=locality_df["name"]

# Need to be removed
countries = ["United Arab Emirates", "Saudi Arabia", "Hong Kong", "Jordan","Japan"]


site_ids = sites_df.site_id
sids = [f"S{n}" for n in range(0,14)]
count_list = [n for n in range(0,1001)]
area_size_list = [n for n in range(0,1001,5)]
# survey_methods=["Reef Check","Photogrammetry", "360 Video", "eDNA"]
project_types = ["Reef Tiles","EcoSeaWall", "Site Assessment","Testing"]
project_keys = ["C","W","A", "T"]
project_dict = dict(zip(project_types,project_keys))


# method need to be updated for the year and locality part

def generate_site_id():
    key = project_dict[project_type]
    client_code = clients_df[clients_df.name == client_name].client_code.iloc[0]
    year = str(deployment_start_date.year)[2:]
    site_id=f"{key}-{client_code}{year}-{lc_code}"
    sids=sites_df.site_id
    sids=sids.apply(lambda sid: sid[0:-3]) 
    site_no=str((len(sids[sids==site_id]) + 1)).zfill(2)
    site_id+=f"-{site_no}"
    return site_id
    
st.set_page_config(page_title="Create Site", page_icon="🌍")

st.markdown("# Create Site")
st.divider()


#Get list of client names
client_names = clients_df.name
agent_names = agents_df.full_name

col1,col2=st.columns(2)

# Column 1 Content
client_name = col1.selectbox(label="Client", options=client_names)
site_name = col1.text_input(label="Site Name")
project_manager = col1.selectbox(label="Project Manager", options=agent_names)
project_type = col1.selectbox(label="Project Type", options=project_types)
deployment_start_date = col1.date_input(label="Deployment Start Date")
deployment_end_date = col1.date_input(label="Deployment End Date")
# site_data=sites[sites.site_id==site_id].iloc[0]
# start_date=col1.date_input(label="Start Date")
# survey_type=col1.selectbox(label="Survey Type", options=["quarterly", "bimonthly","annual"])

# Columnt 2 Content
country = col2.selectbox(label="Country", options=countries)
country=country.strip()
city = col2.text_input(label="City")
quantity = col2.selectbox(label="Quantity", options=count_list)
site_area_m2 = col2.selectbox(label="Site Area (m2)", options=area_size_list)
locality = col2.text_input(label="Locality Name")
lc_code = col2.text_input(label="Locality Code (2 letters)")

# Validation for locality Code
if (locality_df.locality_code == lc_code).any():
    st.error('Locality Code Already Exists in DB! Please try a different code.', icon="❌")
if len(lc_code) != 2:
    st.error('Locality Code must be 2 letters.', icon="❌")


coordinates = st.text_input("GPS Coordinates (Lat, Lon)",  placeholder="Lat, Lon", value="0.0000, 0.0000")
# latitude = col2.text_input("Latitude", placeholder="Latitude...",  value="0.0000")


coordinates = coordinates.split(",")
latitude = float(coordinates[0])
longitude = float(coordinates[1])

map_data = pd.DataFrame(dict(lat=[latitude],lon=[longitude]))
st.markdown(":red[Confirm site location on the map before saving.]")
st.map(map_data, zoom=5)

client_code = clients_df[clients_df.name == client_name].client_code.iloc[0]

site_record = dict(
        site_id=generate_site_id(),
        client_code=client_code,
        site_name=site_name,
        project_manager=project_manager,
        type=project_type,
        start_date=deployment_start_date,
        end_date = deployment_end_date,
        country=country,
        city=city,
        quantity=quantity,
        area_m2=site_area_m2,
        locality_name=locality,
        latitude=latitude,
        longitude=longitude, 
        geo_code=geo_codes[country]
)

submit = st.container(border=True)
submit_btn = st.button("SUBMIT")
output = st.container(border=True)

if submit_btn:
    
        
    # starttime = time.time()
    post_status = post_record(new_record=site_record, source_df=sites_df, store_obj=s3_storage,
                              output_path=site_storage_path)
    # print(time.time() - starttime)
    if post_status:
        output.success("New Site Added Successfully!")
        output.info("Number of Sites: " + str(sites_df.shape[0]))
        output.write(site_record)
    else:
        output.error("Sorry Something Went Wrong, Please Try Again!")

