import streamlit as st
import pandas as pd
import io
import os
import sys
from S3 import Storage
import os.path as path

# Set root path for code modules
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

# Need to be removed
root = path.abspath(path.join(__file__, "../../.."))
countries = pd.read_csv(f'{root}/data/reefops/countries.csv', encoding="ISO-8859-1")

s3_storage = Storage(name='archireef-hive')
# Load the data from aws s3 as binary format
loaded_sites_s3 = s3_storage.read_file(file_path='database/reef_ops/clients.csv')
# Read the binary data
client_obj = io.BytesIO(loaded_sites_s3)
clients_df = pd.read_csv(client_obj)

st.set_page_config(page_title="Create Client", page_icon="🌍")

st.markdown("# Create New Client")
st.divider()


def post_data():
    global clients_df
    client_record = dict(
        name=name,
        client_code=client_code,
        address=address,
        contact_name=contact_name,
        primary_email=contact_email,
        primary_mobile_no=contact_no,
        contact_department=contact_department,
        onboarded=onboarded
    )
    clients_num = clients_df.shape[0]
    # update the new client record id
    client_id = clients_df.iloc[-1]['client_id'] + 1
    clients_df = clients_df._append(client_record, ignore_index=True)
    clients_df.loc[clients_df.index[-1], 'client_id'] = client_id
    clients_df['client_id'] = clients_df['client_id'].astype('int')
    csv_buffer = io.StringIO()
    clients_df.to_csv(csv_buffer, index=False)
    post_result = s3_storage.write_file(binary_data=csv_buffer.getvalue(), output_path='database/reef_ops/clients.csv')
    if post_result['ResponseMetadata']['HTTPStatusCode'] == 200 and clients_df.shape[0] > clients_num:
        output.success("New Client Added Successfully!")
        output.info("Number of Clients: " + str(clients_df.shape[0]))
        output.write(client_record)
    else:
        output.error("Sorry Something Went Wrong, Please Try Again!")


col1, col2 = st.columns(2)

# Column 1 Content
name = col1.text_input(label="Company Name")
client_code = col1.text_input(label="Client Code")
address = col1.text_input(label="Company Address")
contact_name = col1.text_input(label="Contact Name")
contact_no = col1.text_input(label="Contact Number")

# Column 2 Content
country = col2.selectbox(label="Country", options=countries.name.to_list())
city = col2.text_input(label="City")
contact_department = col2.text_input(label="Contact Department")
contact_email = col2.text_input(label="Contact Email")
onboarded = col2.selectbox(label="Client Onboarded?", options=["Yes", "No"])

submit = st.container(border=True)
submit.button("SUBMIT", on_click=post_data)
output = st.container(border=True)
