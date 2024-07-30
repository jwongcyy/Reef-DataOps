import streamlit as st
import pandas as pd
from polyp.ReefOps import time_stage_label
from polyp.config import DATE_STR_FORMAT
from polyp.ReefCheck import ReefCheck
from polyp.ReefOps import Site
import calendar
import datetime
import plotly.express as px
from streamlit_folium import st_folium
import os.path as path


root =  path.abspath(path.join(__file__ ,"../.."))

# Get Operational data
clients=pd.read_csv(f'{root}/data/reefops/clients.csv')
#Get list of client names
client_names=clients.name

sites=pd.read_csv(f'{root}/data/reefops/sites.csv')
surveys=pd.read_csv(f'{root}/data/reefops/surveys.csv')
rsfm_data=pd.read_csv(f'{root}/data/reefsfm/reefsfm_db_coral_metrics.csv')



st.set_page_config(page_title="ReefOps Tool", layout="wide",page_icon=":tropical_fish:")

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

regions=["United Arab Emirates", "Hong Kong"]




# Add a selectbox to the sidebar:
client_selection = st.sidebar.selectbox(
      'Select Client',
      client_names
   )


selected_client=clients[clients.name==client_selection].iloc[0]
selected_site=sites[sites.client_code == selected_client.client_code].iloc[0]


site=Site(selected_site.site_id)
selected_survey=site.surveys.survey_df
selected_survey["start_dt"]=pd.to_datetime(selected_survey.start_date,format=DATE_STR_FORMAT)
selected_survey["end_dt"]=pd.to_datetime(selected_survey.end_date,format=DATE_STR_FORMAT)

st.header(f"{selected_client['name']}")
st.divider()

cl_col1,cl_col2,cl_col3 = st.columns([1,1,3])
cl_col1.subheader("Address")

address=selected_client.address.split(",")
for ad in address:
   cl_col1.write(ad)

cl_col2.subheader("Primary Contact")
cl_col2.write(selected_client.contact_name)
cl_col2.write(selected_client.contact_department)
cl_col2.write(selected_client.primary_mobile_no)
cl_col2.write(selected_client.primary_email)
#    st.write(selected_client.region)



st.divider()
st.header(f"Site: {site.name}")
st.divider()

col1, col2, col3 = st.columns([1,1,3])

# Column 1 content
col1.metric(label="Site ID", value=site.site_id)

col1.metric(label="Deployment Type" , value=site.site_df["type"].replace("_", " ").title())
col1.metric(label="Locality" , value=site.locality)
col1.metric(label="Country" , value=site.site_df.country)
col1.metric(label="City" , value=site.site_df.city)

# Column 2 content
col2.metric(label="Project Manager", value=site.site_df.project_manager)
col2.metric(label="Deployment Start Date" , value=readable_date(site.start_date))
col2.metric(label="Deployment End Date" , value=readable_date(site.end_date))
col2.metric(label="Project Area" , value=f"{int(site.area_m2)} m2")
col2.metric(label="Quantity" , value=int(site.site_df.quantity))

# Column 3 content

map_data = pd.DataFrame(dict(lat= [site.site_df.latitude],lon = [site.site_df.longitude], size=500))
col3.map(map_data)


st.divider()
st.header(f"Survey Information")
st.divider()
col1, col2 = st.columns(2)

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
st.divider()
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
st.header("ReefCheck Data")
st.write("")

rc=ReefCheck(site_id=selected_site.site_id)
st.write(rc.reefcheck_df.drop("site_id", axis =1))


st.divider()
st.header("ReefSFM Data")
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


