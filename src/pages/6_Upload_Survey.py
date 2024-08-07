import streamlit as st
import pandas as pd
import pydeck as pdk
from urllib.error import URLError
import numpy as np
from ReefOps import Site

import os.path as path


root =  path.abspath(path.join(__file__ ,"../../.."))

# Get Operational data
clients=pd.read_csv(f'{root}/data/reefops/clients.csv')
clients=clients[(clients.onboarded==True) & (clients.reeftiles==True)]
sites=pd.read_csv(f'{root}/data/reefops/sites.csv')
agents=pd.read_csv(f'{root}/data/reefops/agents.csv')
countries=pd.read_csv(f'{root}/data/reefops/countries.csv', encoding = "ISO-8859-1")
surveys=pd.read_csv(f'{root}/data/reefops/surveys.csv')
indicator_species=pd.read_csv(f'{root}/data/reefcheck/indicator_species.csv')
species_db=pd.read_csv(f'{root}/data/reefcheck/species_db.csv')

agent_names=agents.full_name
sids=[f"S{n}" for n in range(0,14)]
site_ids=sites.site_id


depth_list=[round(x,1) for x in np.arange(0,50,0.1)]
bearing_list=[x for x in range(0,360)]
gcp_id_list=[f"GCP{str(n).zfill(2)}" for n in range(1, 101)]
survey_methods=["Reef Check","Photogrammetry", "360 Video", "eDNA", "BRUV","Benthic Transect"]
cameras=["GoPro Hero 11", "GoPro Hero12", "Olympus TG-6", "Olympus TG-7", "Nikon Z7II", "Nikon D750", "Nikon D7800"]
survey_data=None

def get_survey_data():
    survey_data=dict(
        site_id=site_id,
        survey_id=survey_id,
        survey_type=survey_type,
        start_date=start_date,
        end_date=end_date,
        agents=agents,
        survey_methods=methods,
        dives=dive_count,
        baseline=baseline,
        transplanting=transplanting,
        exp360_id=exp360_id,
        done = True # should be validated based on date
    )

    submit.subheader("Survey Data")
    submit.write(survey_data)
    submit.subheader("Dive Logs")
    submit.write(dive_logs)
    submit.subheader("Reef Check Data")
    submit.write(rc_data)





st.set_page_config(page_title="Upload Survey Data", layout="wide",page_icon=":tropical_fish:")

st.markdown("# Upload Survey Data")

st.divider()

# upload=st.button("Upload Survey")
# modify=st.button("Modify Data")


# if upload:
#     st.write("Uploading")
#
# if modify:
#     site_id=st.selectbox(label="Modify Site ID", options=site_ids)
#     survey_id=st.selectbox(label="Modify Survey ID", options=sids)
#
#     vals=dict(site_id=site_id,survey_id=survey_id)



#Get list of client names
client_names=clients.name

col1,col2=st.columns(2)
col1.subheader("Survey Metadata")
col2.subheader("Dive Logs")

survey_metadata=st.container(border=True)
sm_col1,sm_col2=survey_metadata.columns(2)


# Column 1 Content
site_id=sm_col1.selectbox(label="Site ID", options=site_ids)
site_data=sites[sites.site_id==site_id].iloc[0]

survey_type=sm_col2.selectbox(label="Survey Type", options=["assessment","quarterly", "bimonthly","annual"])

if survey_type == "assessment":
    sids=["SA"]
else:
    sids=[f"S{n}" for n in range(0,14)]

survey_id=sm_col1.selectbox(label="Survey ID", options=sids)
start_date=sm_col1.date_input(label="Start Date")

methods=survey_metadata.multiselect(label="Survey Methods", options=survey_methods)


# Columnt 2 Content

agents=sm_col2.multiselect(label="Agents", options=agent_names)

end_date=sm_col2.date_input(label="End Date")

survey_metadata.divider()
dive_count=survey_metadata.number_input(label="Number of Dives", value=1)
transplanting=survey_metadata.toggle('Transplanting Implemented')
baseline=survey_metadata.toggle('New Baseline')

st.divider()

st.subheader("Dive Logs")
dive_logs=list()

if dive_count > 0:
    labels=[f"Dive #{n}" for n in range(1,dive_count +1)]
    tabs=st.tabs(labels)
    for i in range(0,len(tabs)):
        data=dict()
        data["site_id"]=site_id
        data["survey_id"]=survey_id
        data["dive_id"] = f"{site_id}-{survey_id}-D{i+1}"
        tab=tabs[i]
        dive_container = tab.container(border=True)
        dl_col1, dl_col2, dl_col3 = dive_container.columns(3)

        data["dive_date"]=dl_col1.date_input(label=f"Date ({labels[i]})")
        data["divers"]=dl_col1.multiselect(label=f"Divers ({labels[i]})", options=agent_names)
        data["start_time"]=dl_col1.time_input(label=f"Start Time ({labels[i]})")
        data["end_time"]=dl_col1.time_input(label= f"End Time ({labels[i]})")

        data["max_depth_m"]=dl_col2.number_input(label=f"Max Depth (m) ({labels[i]})", value=0.0)
        data["min_temp_c"]=dl_col2.number_input(label= f"Min Temp (C) ({labels[i]})", value =0.0)
        data["max_temp_c"]=dl_col2.number_input(label=f"Max Temp (C) ({labels[i]})", value=0.0)

        data["substrate_type"]=dl_col2.text_input(label=f"Substrate Type ({labels[i]})")
        data["remarks"]=dl_col3.text_area(label=f"Remarks ({labels[i]})", height=300)

        data["reefcheck"]=dive_container.toggle(f"Reef Check ({labels[i]})")
        data["sfm"]=dive_container.toggle(f"Photogrammetry ({labels[i]})")


        if data["reefcheck"]:
            rc_container = dive_container.container(border=True)
            rc_container.header("Reef Check Metadata")
            rc_col1,rc_col2 = rc_container.columns(2)
        
            rc_col1.subheader("Hive Metadata")
            data["rc_hive_start_time"]=rc_col1.time_input(label=f"Hive Start Time ({labels[i]})")
            data["rc_hive_end_time"]=rc_col1.time_input(label= f"Hive End Time ({labels[i]})")
            # rc_hive_duration = rc_hive_end_time - rc_hive_start_time
            data["rc_hive_depth"]=rc_col1.number_input(label=f"Hive Max Depth (m) ({labels[i]})", value=0.0)
            data["rc_hive_temperature"]=rc_col1.number_input(label= f"Hive Temp (C) ({labels[i]})", value=0.0)
            data["rc_hive_visibility_m"]=rc_col1.number_input(label= f"Hive Visibility (m) ({labels[i]})", value=0)
            data["rc_hive_divers"]=dive_agents=rc_col1.multiselect(label= f"Hive Divers ({labels[i]})", options=agent_names)

            rc_col2.subheader("Control Metadata")
            data["rc_control_start_time"]=rc_col2.time_input(label= f"Control Start Time ({labels[i]})")
            data["rc_control_end_time"]=rc_col2.time_input(label= f"Control End Time ({labels[i]})")
            # data["rc_control_duration"] = data["rc_control_end_time"] - data["rc_control_start_time"]
            data["rc_control_depth"]=rc_col2.number_input(label= f"Control Max Depth (m) ({labels[i]})", value=0.0)
            data["rc_control_temperature"]=rc_col2.number_input(label= f"Control Temp (C) ({labels[i]})", value=0.0)
            data["rc_control_visibility_m"]=rc_col2.number_input(label= f"Control Visibility (m) ({labels[i]})", value=0)
            data["rc_control_divers"]=rc_col2.multiselect(label=f"Control Divers ({labels[i]})", options=agent_names)

        if data["sfm"]:
            sfm_container = dive_container.container(border=True)
            sfm_container.header("Photogrammetry Metadata")
            sfm_col1,sfm_col2 = sfm_container.columns(2)
            sfm_col1.subheader("SFM Survey Metadata")
            data["sfm_diver_1"]=sfm_col1.selectbox(label=f"SFM Diver 1 ({labels[i]})", options=agent_names)
            data["sfm_diver_2"]=sfm_col1.selectbox(label=f"SFM Diver 2 ({labels[i]})", options=agent_names)
            data["sfm_start_time"]=sfm_col1.time_input(label= f"SFM Start Time ({labels[i]})")
            data["sfm_end_time"]=sfm_col1.time_input(label= f"SFM End Time ({labels[i]})")
            data["sfm_camera"]=sfm_col1.selectbox(label=f"Camera Model ({labels[i]})", options=cameras)
            data["sfm_stereo"]=sfm_col1.selectbox(label=f"Stereo Rig ({labels[i]})", options=["Yes", "No"])
            data["sfm_lights"]=sfm_col1.selectbox(label=f"Lights ({labels[i]})", options=["Yes", "No"])
            

            sfm_col2.subheader("GCP Metadata")
            gcp_count=10
            data["reference_gcp_id"]= sfm_col2.selectbox(label=f"Reference Marker ID ({labels[i]})", options=gcp_id_list)
            data["reference_gcp_coords"]= sfm_col2.text_input(label=f"GPS Coordinates of Reference Marker (Lat, Lon) ({labels[i]})")
    
            gcp_data=dict(
                gcp_id=gcp_id_list,
                depth_m=[0.0 for x in range(0,len(gcp_id_list))],
                bearing=[0 for x in range(0,len(gcp_id_list))],
                reference=[True if gcp == data["reference_gcp_id"] else False for gcp in gcp_id_list ]
            )
            
            data["gcp_log"]=sfm_col2.data_editor(
                gcp_data, 
                num_rows="dynamic", 
                key=f"{labels[i]}",
                width= 700,
                column_config={
                    "depth_m": st.column_config.SelectboxColumn(
                        "Depth (m)",
                        help="Enter the Depth of the GCP to the 0.1 m level.",
                        width="medium",
                        options=depth_list,
                        required=False,
                    ),
                    "bearing": st.column_config.SelectboxColumn(
                        "Reference Bearing (°)",
                        help="North Bearing from reference marker to a given GCP.",
                        width="medium",
                        options=bearing_list,
                        required=False,
                    ),
                    "reference": st.column_config.CheckboxColumn(
                        "Is Reference",
                        help="Marks the Reference Marker.",
                        width="medium",
                        # options=bearing_list,
                        required=True,
                    )}
            )

            
        dive_logs.append(data)
        


st.divider()
# Reef Check Data Upload
st.header("ReefCheck Data")

geo_code=site_data.geo_code.lower()
df=pd.DataFrame(index=[n for n in range(0,11)], columns=["species","treatment","count","min_length_cm","max_length_cm","mean_length_cm"])
df["species"] = ""
df["treatment"]=""
df["count"] = 0 
df["min_length_cm"] = 0 
df["max_length_cm"] = 0 
df["mean_length_cm"] = 0 


species_list=species_db.species
count_list=[n for n in range(0,1001)]

rc_data=st.data_editor(
    df,
    num_rows="dynamic",
    column_config={
        "species": st.column_config.SelectboxColumn(
            "Species",
            help="The category of the app",
            width="medium",
            options=species_list,
            required=False,
        ),
        "count": st.column_config.SelectboxColumn(
            "Count",
            help="The category of the app",
            width="small",
            options=count_list,
            required=False,
        ),
        "treatment": st.column_config.SelectboxColumn(
            "Treatment",
            help="The category of the app",
            width="medium",
            options=["Hive", "Control"],
            required=False,
        ),
        "min_length_cm": st.column_config.SelectboxColumn(
            "Min Length (cm)",
            help="The category of the app",
            width="medium",
            options=count_list,
            required=False,
        ),
        "max_length_cm": st.column_config.SelectboxColumn(
            "Max Length (cm)",
            help="The category of the app",
            width="medium",
            options=count_list,
            required=False,
        ),
        "mean_length_cm": st.column_config.SelectboxColumn(
            "Mean Length (cm)",
            help="The category of the app",
            width="medium",
            options=count_list,
            required=False,
        )
    },
    hide_index=False,
    key="hive"
)

site=Site(site_id=site_id)
show_img=st.toggle(label="Show Indicator Species Photos")
if show_img:
    img_gallery=st.container(border=True)
    img_path=f"{root}/data/reefcheck/images"
    region_species=indicator_species[indicator_species[site.geo_code.lower()] == True].reset_index()
    region_species["img"]=[f"{img_path}/{sp.lower().replace(' ', '_').replace('.','')}.jpg" for sp in region_species.species]
    cols=5
    rows=len(region_species) / 5
    if rows > int(rows):
        rows=int(rows) +1
    else:
        rows=int(rows)
    n=0
    shape=[cols, rows]

    col_count=0

    for r in range(0,rows):
        row=img_gallery.container()
        d=region_species.iloc[n:n+cols]
        img=d.img
        sp=d.species
        co=d.common_name

        for col,i,s,c in zip(row.columns(cols), img,sp,co):
            try:
                
                col.image(i)
                col.markdown(f"### *{s}*")
                col.markdown(f"*{c}*")
            except:
                col.markdown(f"### *{s}*")
                col.markdown(f"*{c}*")
                continue

        n+=cols





st.header("360 Video")

exp360_id=st.text_input(label="EXP360 Video ID")


submit=st.container(border=True)
submit.button("SUBMIT", on_click=get_survey_data)




