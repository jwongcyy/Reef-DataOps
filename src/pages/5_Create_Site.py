import streamlit as st
import pandas as pd
import datetime
import os.path as path


root =  path.abspath(path.join(__file__ ,"../../.."))

# Get Operational data
clients=pd.read_csv(f'{root}/data/reefops/clients.csv')
sites=pd.read_csv(f'{root}/data/reefops/sites.csv')
agents=pd.read_csv(f'{root}/data/reefops/agents.csv')
countries=pd.read_csv(f'{root}/data/reefops/countries.csv', encoding = "ISO-8859-1")



agent_names=agents.full_name

site_ids=sites.site_id
sids=[f"S{n}" for n in range(0,14)]
count_list=[n for n in range(0,1001)]
area_size_list=[n for n in range(0,1001,5)]
# survey_methods=["Reef Check","Photogrammetry", "360 Video", "eDNA"]
project_types=["Reef Tiles","EcoSeaWall", "Site Assessment"]
project_keys=["C","W","A"]
project_dict=dict(zip(project_types,project_keys))

lc='locality'

def generate_site_id():
    key=project_dict[project_type]
    client_code=clients[clients.name==client_name].client_code.iloc[0]
    date=datetime.datetime.now()
    year=str(date.year)[2:]
    return f"{key}-{client_code}{year}-{lc}-01"
    
st.set_page_config(page_title="Create Site", page_icon="🌍")

st.markdown("# Create Site")
st.divider()



def get_data():
    data=dict(
        site_id=generate_site_id(),
        client_name=client_name,
        site_name=site_name,
        project_manager=project_manager,
        project_type=project_type,
        deployment_start_date=deployment_start_date,
        deployment_end_date = deployment_end_date,
        country=country,
        quantity=quantity,
        site_area_m2=site_area_m2,
        locality=locality,
        latitude=latitude,
        longitude=longitude

    )
    submit.write(data)
#Get list of client names
client_names=clients.name

col1,col2=st.columns(2)


# Column 1 Content
client_name=col1.selectbox(label="Client", options=client_names)
site_name=col1.text_input(label="Site Name")
project_manager=col1.selectbox(label="Project Manager", options=agent_names)
project_type=col1.selectbox(label="Project Type", options=project_types)
deployment_start_date=col1.date_input(label="Deployment Start Date")
deployment_end_date=col1.date_input(label="Deployment End Date")
# site_data=sites[sites.site_id==site_id].iloc[0]
# start_date=col1.date_input(label="Start Date")
# survey_type=col1.selectbox(label="Survey Type", options=["quarterly", "bimonthly","annual"])

# Columnt 2 Content
country=col2.selectbox(label="Country", options=countries.name.to_list())
quantity=col2.selectbox(label="Quantity", options=count_list)
site_area_m2=col2.selectbox(label="Site Area (m2)", options=area_size_list)
locality=col2.text_input(label="Locality Name")
longitude = col2.text_input("Longitude",  placeholder="Longitude...", value="0.0000")
latitude = col2.text_input("Latitude", placeholder="Latitude...",  value="0.0000")


latitude=float(latitude)
longitude=float(longitude)

map_data = pd.DataFrame(dict(lat= [latitude],lon = [longitude]))
st.map(map_data)

submit=st.container(border=True)
submit.button("SUBMIT",on_click=get_data)