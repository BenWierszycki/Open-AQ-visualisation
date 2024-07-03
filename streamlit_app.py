import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import psycopg2 as psql
import os
import matplotlib.dates as mdates
from datetime import datetime, timedelta

from functions import get_all_pollutants_uk
from functions import get_single_pollutant

from fetching_from_SQL import get_latest_pollutants_uk
from fetching_from_SQL import get_av_last_7_days
from fetching_from_SQL import get_av_last_year
from fetching_from_SQL import get_latest_pollutants_global

username = st.secrets['username']
password = st.secrets['password']
host = st.secrets['host']
dbname = st.secrets['dbname']
port = st.secrets['port']


all_locations = ['London Westminster',
                   'London Hillingdon',
                     'Oxford', 
                     'Manchester', 
                     'Lima', 
                     'Karachi', 
                     'Singapore' ]

uk_locations = ['London Westminster',
                   'London Hillingdon',
                     'Oxford', 
                     'Manchester']

global_locations = [ 'Lima', 
                     'Karachi', 
                     'Singapore' ]

city_countries = {
    'London Westminster': 'united%20kingdom',
    'London Hillingdon': 'united%20kingdom',
    'Oxford': 'united%20kingdom',
    'Manchester': 'united%20kingdom',
    'Lima': 'peru',
    'Karachi': 'pakistan',
    'Singapore': 'singapore'
}

city_countries = {
    'London Westminster': 'united%20kingdom',
    'London Hillingdon': 'united%20kingdom',
    'Oxford': 'united%20kingdom',
    'Manchester': 'united%20kingdom',
    'Lima': 'peru',
    'Karachi': 'pakistan',
    'Singapore': 'singapore'
}

city_alternate_names = {    
    'London Westminster': 'Westminster',
    'London Hillingdon': 'Hillingdon',
    'Oxford':'Oxford',
    'Manchester': 'Manchester',
    'Lima': 'Lima',
    'Karachi': 'Karachi',
    'Singapore': 'Singapore'}

time_frame_to_days = {    
    'Last 24 hours' : 1,
    'Last 7 days' : 7,
    'Last Month' : 30,
    'Last Year' : 365}

pollution_paramters = ['All','PM 2.5', 'O3', 'NO2']

st.title("Open AQ Air Pollution Data")

st.write(
    "Use this App to investigate air pollution data for cities in the UK and across the world!"
)

# choose UK or Global City ####################################################
st.write('')
uk_or_global_choice = st.radio("UK or Global Location?", options = ['UK', 'Global'])

# -----------------------------------------------------------------------------------
# If UK location chosen:

if uk_or_global_choice == 'UK':
    uk_locations_choice = st.selectbox('Choose a location', uk_locations)
    country = city_countries.get(uk_locations_choice)
    flags_url = f'https://restcountries.com/v3.1/name/{country.lower()}'
    response = requests.get(flags_url)
    flags = response.json()
    flag_image = flags[0]['flags']['png']

# displaying location name and flag
    st.write('')
    st.write('')
    name_col, flag_col = st.columns([1,1])
    with name_col:
        country_selected = st.title(uk_locations_choice.title())
    with flag_col:
        st.image(flag_image, width = 150)
    
    st.write('')

    paramater_choice = st.selectbox('Choose pollution parameter', pollution_paramters)
    st.write('')
    st.write('')

    renamed_city = city_alternate_names.get(uk_locations_choice)
    latest_pollutant_data = get_latest_pollutants_uk(renamed_city, paramater_choice)

    if paramater_choice == 'All':
        
        pollutant_col1, pollutant_col2, pollutant_col3 = st.columns(3)
        with pollutant_col1:
            st.metric(label = f"Latest PM 2.5 µg/m³", 
                        value = [latest_pollutant_data][0]['latest_pm25'], 
                        delta = ([latest_pollutant_data][0]['latest_pm25'])-([latest_pollutant_data][0]['second_latest_pm25']),
                        delta_color = 'inverse')
        with pollutant_col2:
            st.metric(label = f"Latest O3 µg/m³", 
                        value = [latest_pollutant_data][0]['latest_o3'], 
                        delta = ([latest_pollutant_data][0]['latest_o3'])-([latest_pollutant_data][0]['second_latest_o3']),
                        delta_color = 'inverse')
        with pollutant_col3:
            st.metric(label = f"Latest NO2 µg/m³", 
                        value = [latest_pollutant_data][0]['latest_no2'], 
                        delta = ([latest_pollutant_data][0]['latest_no2'])-([latest_pollutant_data][0]['second_latest_no2']),
                        delta_color = 'inverse')
            
        st.write(' ')
        st.write('')
        desired_timeframe = st.select_slider('Select Timeframe', options=['Last 24 hours','Last 7 days', 'Last Month', 'Last Year'])
        timeframe = time_frame_to_days.get(desired_timeframe)
        st.write('')
        st.write('')
        st.write('')
        get_all_pollutants_uk(renamed_city, timeframe)


    else:
        if paramater_choice == 'PM 2.5':
            paramater_choice = 'pm25'

        pollutant_col1, pollutant_col2, pollutant_col3 = st.columns(3)
        with pollutant_col1:
            st.metric(label = f"Latest {paramater_choice.upper()} µg/m³", 
                        value = round([latest_pollutant_data][0][f'latest_{paramater_choice.lower()}'],1), 
                        delta = round(([latest_pollutant_data][0][f'latest_{paramater_choice.lower()}'])-([latest_pollutant_data][0][f'second_latest_{paramater_choice.lower()}']),1),
                        delta_color = 'inverse')
        with pollutant_col2:
            st.metric(label = f"7 day average {paramater_choice.upper()} µg/m³",
                      value = round(get_av_last_7_days(renamed_city, paramater_choice), 1))
        with pollutant_col3:
            st.metric(label = f"Year average {paramater_choice.upper()} µg/m³",
                      value = round(get_av_last_year(renamed_city, paramater_choice), 1))  
        
        st.write(' ')
        st.write('')
        desired_timeframe = st.select_slider('Select Timeframe', options=['Last 24 hours','Last 7 days', 'Last Month', 'Last Year'])
        timeframe = time_frame_to_days.get(desired_timeframe)  
        st.write('')
        st.write('') 
        get_single_pollutant(renamed_city, timeframe, paramater_choice)
    
#--------------------------------------------------------------------------------------------
# If Global location chosen

else:
    global_locations_choice = st.selectbox('Choose a location', global_locations)
    country = city_countries.get(global_locations_choice)
    renamed_city = city_alternate_names.get(global_locations_choice)
    latest_pollutant_data = get_latest_pollutants_global(renamed_city)

    flags_url = f'https://restcountries.com/v3.1/name/{country.lower()}'
    response = requests.get(flags_url)
    flags = response.json()
    flag_image = flags[0]['flags']['png']

# displaying location name and flag
    st.write('')
    st.write('')
    name_col, flag_col = st.columns(2)
    with name_col:
        country_selected = st.title(global_locations_choice.title())
    with flag_col:
        st.image(flag_image, width = 150)

    st.write('')
    st.write('')

    
    paramater_choice = 'pm25'
    latest_pollutant_data = get_latest_pollutants_global(renamed_city)

    pollutant_col1, pollutant_col2, pollutant_col3 = st.columns(3)
    with pollutant_col1:
        st.metric(label = f"Latest PM 2.5 µg/m³", 
                    value = round([latest_pollutant_data][0]['latest_pm25'],1), 
                    delta = round(([latest_pollutant_data][0]['latest_pm25'])-([latest_pollutant_data][0]['second_latest_pm25']),1),
                    delta_color = 'inverse')
    with pollutant_col2:
        st.metric(label = f"7 day average PM 2.5 µg/m³",
                    value = round(get_av_last_7_days(renamed_city,paramater_choice), 1))
    with pollutant_col3:
        st.metric(label = f"Year average PM 2.5 µg/m³",
                    value = round(get_av_last_year(renamed_city,paramater_choice), 1)) 
    
    st.write(' ')
    st.write('')
    desired_timeframe_2 = st.select_slider('Select Timeframe', options=['Last 24 hours','Last 7 days', 'Last Month', 'Last Year'])
    timeframe = time_frame_to_days.get(desired_timeframe_2)
    st.write('')
    st.write('') 
    get_single_pollutant(renamed_city, timeframe, paramater_choice)





st.write('')
st.write('')
st.write('')
st.write('')















