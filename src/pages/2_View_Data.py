import streamlit as st
import pandas as pd

import os.path as path

st.set_page_config(page_title="View Data", layout="wide",page_icon=":tropical_fish:")

root =  path.abspath(path.join(__file__ ,"../../.."))
# Get Operational data
clients=pd.read_csv(f'{root}/data/reefops/clients.csv').fillna("")
sites=pd.read_csv(f'{root}/data/reefops/sites.csv').fillna("")
surveys=pd.read_csv(f'{root}/data/reefops/surveys.csv').fillna("")
agents=pd.read_csv(f'{root}/data/reefops/agents.csv').fillna("")
reefcheck_df=pd.read_csv(f'{root}/data/reefcheck/reefcheck_db.csv').fillna("")
reefsfm_reef=pd.read_csv(f'{root}/data/reefsfm/reefsfm_db_coral_metrics.csv').fillna("")
reefsfm_coral=pd.read_csv(f'{root}/data/reefsfm/reefsfm_db_reef_metrics.csv').fillna("")
countries=pd.read_csv(f'{root}/data/reefops/countries.csv', encoding = "ISO-8859-1")


site_ids=sites.site_id
sids=[f"S{n}" for n in range(0,14)]
count_list=[n for n in range(0,1001)]
# survey_methods=["Reef Check","Photogrammetry", "360 Video", "eDNA"]
project_types=["Reef Tiles","EcoSeaWall", "Site Assessment"]
data_types=["Clients", "Sites", "Surveys", "Agents","ReefCheck DB", "ReefSFM Metrics [Reef Level]", "ReefSFM Metrics [Colony Level]"]
datasets=[clients,sites, surveys,agents, reefcheck_df, reefsfm_reef, reefsfm_coral]
datasets=dict(zip(data_types,datasets))

st.markdown("# Database Viewer")
st.divider()



# Add a selectbox to the sidebar:
data_type = st.selectbox(
      'Select Client',
      data_types
   )

st.dataframe(datasets[data_type])