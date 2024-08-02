import streamlit as st


import numpy as np
import pandas as pd
from ReefOps import time_stage_label
from config import DATE_STR_FORMAT
import calendar
import datetime
from ReefCheck import ReefCheck
from ReefOps import Site
import plotly.express as px
from streamlit_folium import st_folium
import os.path as path
import folium


from streamlit_folium import st_folium



root =  path.abspath(path.join(__file__ ,"../.."))

# Get Operational data
clients=pd.read_csv(f'{root}/data/reefops/clients.csv')
#Get list of client names
client_names=clients.name

sites=pd.read_csv(f'{root}/data/reefops/sites.csv')
site_names=sites.site_name
surveys=pd.read_csv(f'{root}/data/reefops/surveys.csv')
rsfm_data=pd.read_csv(f'{root}/data/reefsfm/reefsfm_db_coral_metrics.csv')



st.set_page_config(page_title="Home - Reef DataOps", layout="wide",page_icon=":tropical_fish:")

def readable_date(date):
    return f"{date.day} {calendar.month_abbr[date.month]}, {date.year}"
    
# Function to get survey data for pretty view
def get_survey_content(sdata):
    output=sdata.apply(lambda x: x.to_dict(), axis = 1).to_list()
    output = [dict(zip(x.keys(),x.values())) for x in output]
    return output

def format_bool(bool):
   if bool == True:
       return ":white_check_mark:"
   else:
       return ":x:"

regions=["United Arab Emirates", "Hong Kong", "Saudi Arabia"]



# Add a selectbox to the sidebar:
site_selection = st.sidebar.selectbox(
      'Select Site',
      site_names
   )



selected_site=sites[sites.site_name == site_selection].iloc[0]
selected_client=clients[clients.client_code==selected_site.client_code].iloc[0]


site=Site(selected_site.site_id)
selected_survey=site.surveys.survey_df
selected_survey["start_dt"]=pd.to_datetime(selected_survey.start_date,format=DATE_STR_FORMAT)
selected_survey["end_dt"]=pd.to_datetime(selected_survey.end_date,format=DATE_STR_FORMAT)


head1,head2=st.columns([1,2])
head1.header(f"{selected_site.site_name}")
head1.markdown(f"**Site ID:** {site.site_id}")
# Column 3 content
head2.write("")

with st.popover("Show Location 🌍"):
    map_data = pd.DataFrame(dict(lat= [site.site_df.latitude],lon = [site.site_df.longitude], size=20))
    # center on Liberty Bell, add marker
    m = folium.Map(location=[site.site_df.latitude, site.site_df.longitude], zoom_start=3,tiles=None)
    folium.CircleMarker(
    location=[site.site_df.latitude,site.site_df.longitude],
    radius=10,
    color="red",
    stroke=False,
    fill=True,
    fill_opacity=1,
    opacity=1,
    # popup="{} pixels".format(radius),
    tooltip=selected_site.site_name,
    ).add_to(m)

    tile = folium.TileLayer(
        tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr = 'Esri',
        name = 'Esri Satellite',
        overlay = False,
        control = True
       ).add_to(m)
    # call to render Folium map in Streamlit
    st_data = st_folium(m,width=310, height= 300)
    # st.map(map_data, use_container_width =True, zoom=1)


st.divider()


col1, col2, col3 = st.columns([1.5,1.5,2])



col1.metric(label="Client" , value=selected_client["name"])
col1.metric(label="Deployment Type" , value=site.site_df["type"].replace("_", " ").title())
col1.metric(label="Deployment Start Date" , value=readable_date(site.start_date))
col1.metric(label="Deployment End Date" , value=readable_date(site.end_date))



# Column 2 content
col2.metric(label="Country" , value=site.site_df.country)
col2.metric(label="City" , value=site.site_df.city)
col2.metric(label="Locality" , value=site.locality)
col2.metric(label="Project Manager", value=site.site_df.project_manager)

scol1,scol2=col3.columns([1,1])
scol1.metric(label="Project Area" , value=f"{int(site.area_m2)} m2")
scol2.metric(label="Quantity" , value=int(site.site_df.quantity))
client_details=col3.container(border=True)
client_details.subheader("Client Contact Info")

client_details.markdown(f"**{selected_client.contact_name}**")

client_details.markdown(f"{selected_client.contact_department}")
client_details.write(f"{selected_client.primary_mobile_no} | {selected_client.primary_email}")
client_details.write(f"{selected_client.address}")







st.divider()
surv1,surv2=st.columns([1,2])
surv1.write("")
surv1.write("")
surv1.write("")
surv1.header(f"Survey Information")
st.divider()

col1, col2 = surv2.columns(2)

completed_surveys=selected_survey[selected_survey.done == True].sort_values("end_dt", ascending = True).reset_index(drop=True)
upcoming_surveys=selected_survey[selected_survey.done == False].sort_values("start_dt").reset_index(drop=True)

last_survey=completed_surveys.iloc[-1]
last_survey_date=time_stage_label(last_survey.survey_id, last_survey.end_date)

next_survey=upcoming_surveys.iloc[0]
next_survey_date=time_stage_label(next_survey.survey_id, next_survey.start_date)

col1.metric(label="Completed Surveys", value=len(completed_surveys))
col1.metric(label=f"Last Survey", value=last_survey_date)


col2.metric(label="Remaining Surveys", value=len(upcoming_surveys))
col2.metric(label=f"Next Survey", value=next_survey_date)
st.subheader(":white_check_mark: Completed Surveys")
st.write("")

# Pull tab content from server
completed_surveys_content = get_survey_content(completed_surveys)
# Create tabs
n_cols = len(completed_surveys_content)
cols = st.columns(n_cols)
 
# Iterate through each tab and build content
for col, s_content in zip(cols, completed_surveys_content):
    with col:
        date = s_content['end_dt']
        cont=col.container(border=True)
        cont.header(s_content['survey_id'])
        cont.subheader(f"{date.day} {calendar.month_abbr[date.month]}, {date.year}")
        cont.markdown(f"**{s_content['survey_type'].title()}**")
        cont.write(s_content["agents"])
        cont.markdown(f"{format_bool(s_content['reef_check'])} **ReefCheck**")
        cont.markdown(f"{format_bool(s_content['sfm'])} **Photogrammetry**")
        cont.markdown(f"{format_bool(s_content['vid360'])} **360 Video:**")

st.divider()
st.subheader(":date: Upcoming Surveys")
st.write("")


# Pull tab content from server
upcoming_surveys_content = get_survey_content(upcoming_surveys[upcoming_surveys.start_date.isnull() == False].head())
# Create tabs
n_cols = len(upcoming_surveys_content)
cols = st.columns(n_cols)
 
now = datetime.datetime.now()
# Iterate through each tab and build content
for col, s_content in zip(cols, upcoming_surveys_content):
    with col:
        date = s_content['start_dt']
        cont=col.container(border=True)
        cont.header(s_content['survey_id'])
        cont.subheader(f"{date.day} {calendar.month_abbr[date.month]}, {date.year}")
        cont.markdown(f"**{s_content['survey_type'].title()}**")
        
        time_delta = date- now
        cont.write(f"{time_delta.days} remaining days")

st.divider()
st.header("🐠 ReefCheck Data")
st.write("")

rc=ReefCheck(site_id=selected_site.site_id)
st.write(rc.reefcheck_df.drop("site_id", axis =1))


st.divider()
st.header("📈 ReefSFM Data")
st.write("")
rs_col1,rs_col2 = st.columns(2)
rs_col1.subheader("Size Distributions")
rs_col2.subheader("Dataset")
rs_col2.write("")
rsfm_data=rsfm_data[rsfm_data.site_id == selected_site.site_id]

if len(rsfm_data) > 0: 
   
   corals_df=pd.read_csv(f"{root}/data/reefsfm/coral_masks.csv")
   
   sl_col1,sl_col2=rs_col1.columns(2)
   
   sid=sl_col1.selectbox(label="Survey ID", options = corals_df.survey_id.unique())
   corals_df=corals_df.set_index("survey_id").loc[sid].reset_index()
   taxa=sl_col2.selectbox(label="Taxa", options = corals_df.taxa.unique())
   corals_df=corals_df[corals_df.taxa ==taxa]
   fig = px.histogram(corals_df, x="area_cm2", labels=dict(area_cm2="Area (cm2)", y="Count"))

   rs_col1.plotly_chart(fig)
   rs_col2.write(rsfm_data)
else:
    st.write("No ReefSFM Data Available")


