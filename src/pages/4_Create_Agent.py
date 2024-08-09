import streamlit as st
import pandas as pd
import pydeck as pdk
from urllib.error import URLError
import io
import os
import sys
from S3 import Storage
import os.path as path
from helper import *

# Set root path for code modules
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

# root = path.abspath(path.join(__file__ ,"../../.."))
# # Get Operational data
# clients=pd.read_csv(f'{root}/data/reefops/clients.csv')

agent_storage_path = 'database/reef_ops/agents.csv'
s3_storage = Storage(name='archireef-hive')
# Load the data from aws s3 as binary format
loaded_agents_s3 = s3_storage.read_file(file_path=agent_storage_path)
# Read the binary data
agent_obj = io.BytesIO(loaded_agents_s3)
agents_df = pd.read_csv(agent_obj)

st.set_page_config(page_title="Create Agent", page_icon="🌍")

st.markdown("# Create Agent")
st.divider()

# #Get list of client names
# client_names = clients.name

col1, col2 = st.columns(2)
# Add a selectbox to the sidebar:

# Column 1 Content
f_name = col1.text_input(label="First Name")
l_name = col2.text_input(label="Last Name")
abbreviation = col1.text_input(label="Abbreviation")
job_title = col2.text_input(label="Job Title")
#company = col2.text_input(label="Company Name")
full_name = f"{f_name} {l_name}"
agent_record = dict(
        first_name=f_name,
        last_name=l_name,
        full_name=full_name,
        abbreviation=abbreviation,
        job_title=job_title,
)

# Columnt 2 Content
submit = st.container(border=True)
submit_btn = st.button("SUBMIT")
output = st.container(border=True)

if submit_btn:
    # starttime = time.time()
    post_status = post_record(new_record=agent_record, source_df=agents_df, store_obj=s3_storage,
                              output_path=agent_storage_path, df_id='agent_id')
    # print(time.time() - starttime)
    if post_status:
        output.success("New Agent Added Successfully!")
        output.info("Number of Agents: " + str(agents_df.shape[0]))
        output.write(agent_record)
    else:
        output.error("Sorry Something Went Wrong, Please Try Again!")
