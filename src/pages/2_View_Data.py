import streamlit as st
import pandas as pd
import io
from S3 import Storage
import os.path as path

st.set_page_config(page_title="View Data", layout="wide",page_icon=":tropical_fish:")

root =  path.abspath(path.join(__file__ ,"../../.."))
# Get Operational data
# clients=pd.read_csv(f'{root}/data/reefops/clients.csv').fillna("")
# agents=pd.read_csv(f'{root}/data/reefops/agents.csv').fillna("")
# sites=pd.read_csv(f'{root}/data/reefops/sites.csv').fillna("")
surveys=pd.read_csv(f'{root}/data/reefops/surveys.csv').fillna("")
reefcheck_df=pd.read_csv(f'{root}/data/reefcheck/reefcheck_db.csv').fillna("")
reefsfm_reef=pd.read_csv(f'{root}/data/reefsfm/reefsfm_db_coral_metrics.csv').fillna("")
reefsfm_coral=pd.read_csv(f'{root}/data/reefsfm/reefsfm_db_reef_metrics.csv').fillna("")
countries=pd.read_csv(f'{root}/data/reefops/countries.csv', encoding = "ISO-8859-1")

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


site_ids=sites_df.site_id
sids=[f"S{n}" for n in range(0,14)]
count_list=[n for n in range(0,1001)]
# survey_methods=["Reef Check","Photogrammetry", "360 Video", "eDNA"]
project_types=["Reef Tiles","EcoSeaWall", "Site Assessment"]
data_types=["Clients", "Agents", "Sites", "Surveys", "ReefCheck DB", "ReefSFM Metrics [Reef Level]", "ReefSFM Metrics [Colony Level]"]
datasets=[clients_df, agents_df, sites_df, surveys, reefcheck_df, reefsfm_reef, reefsfm_coral]
datasets=dict(zip(data_types,datasets))

st.markdown("# Database Viewer")
st.divider()



# Add a selectbox to the sidebar:
data_type = st.selectbox(
      'Select Client',
      data_types
   )

st.dataframe(datasets[data_type])