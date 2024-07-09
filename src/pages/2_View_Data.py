import streamlit as st
import pandas as pd

import os.path as path

st.set_page_config(page_title="View Data", layout="wide",page_icon=":tropical_fish:")

root =  path.abspath(path.join(__file__ ,"../../.."))
# Get Operational data
clients=pd.read_csv(f'{root}/data/reefops/clients.csv').fillna("")
sites=pd.read_csv(f'{root}/data/reefops/sites.csv').fillna("")
countries=pd.read_csv(f'{root}/data/reefops/countries.csv', encoding = "ISO-8859-1")


site_ids=sites.site_id
sids=[f"S{n}" for n in range(0,14)]
count_list=[n for n in range(0,1001)]
# survey_methods=["Reef Check","Photogrammetry", "360 Video", "eDNA"]
project_types=["Reef Tiles","EcoSeaWall", "Site Assessment"]
data_types=["Clients", "Sites"]
datasets=[clients,sites]
datasets=dict(zip(data_types,datasets))

st.markdown("# Create New Client")
st.divider()



# Add a selectbox to the sidebar:
data_type = st.selectbox(
      'Select Client',
      data_types
   )

st.table(datasets[data_type])