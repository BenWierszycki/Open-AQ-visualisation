import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import psycopg2 as psql
import os
import matplotlib.dates as mdates
from datetime import datetime, timedelta

from pollution_graph_functions import get_all_pollutants_uk
from pollution_graph_functions import get_single_pollutant
from pollution_graph_functions import compare_cities_pollutant

from pollution_value_functions import get_latest_pollutants_uk
from pollution_value_functions import get_av_last_7_days
from pollution_value_functions import get_av_last_year
from pollution_value_functions import get_latest_pollutants_global

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
pollution_paramters_2 = ['PM 2.5', 'O3', 'NO2']

st.title("Open AQ Air Pollution Data")

st.write('')
st.write('')

st.write(
    "Use this App to investigate air pollution data for cities in the UK and across the world!"
)

# choose UK or Global City ####################################################
st.write('')
uk_or_global_choice = st.radio("UK or Global Location?", options = ['UK', 'Global'])
st.write('')
st.write('')

# -----------------------------------------------------------------------------------
# If UK location chosen:

if uk_or_global_choice == 'UK':
    locations_choice = st.selectbox('Choose a location', uk_locations)
    country = city_countries.get(locations_choice)
    flags_url = f'https://restcountries.com/v3.1/name/{country.lower()}'
    response = requests.get(flags_url)
    flags = response.json()
    flag_image = flags[0]['flags']['png']

# displaying location name and flag
    st.write('')
    st.write('')
    name_col, flag_col = st.columns([2,1])
    with name_col:
        country_selected = st.title(locations_choice.title())
    with flag_col:
        st.image(flag_image, width = 150)
    
    st.write('')

    parameter_choice = st.selectbox('Choose pollution parameter', pollution_paramters)
    st.write('')
    st.write('')

    renamed_city = city_alternate_names.get(locations_choice)
    latest_pollutant_data = get_latest_pollutants_uk(renamed_city, parameter_choice)

    if parameter_choice == 'All':
        
        st.subheader(f'{renamed_city} latest data (µg/m³):')
        st.write('')

        pollutant_col1, pollutant_col2, pollutant_col3 = st.columns(3)
        with pollutant_col1:
            st.metric(label = f"Latest PM 2.5", 
                        value = round([latest_pollutant_data][0]['latest_pm25'],1), 
                        delta = round(([latest_pollutant_data][0]['latest_pm25'])-([latest_pollutant_data][0]['second_latest_pm25']),1),
                        delta_color = 'inverse')
        with pollutant_col2:
            st.metric(label = f"Latest O3", 
                        value = round([latest_pollutant_data][0]['latest_o3'],1), 
                        delta = round(([latest_pollutant_data][0]['latest_o3'])-([latest_pollutant_data][0]['second_latest_o3']),1),
                        delta_color = 'inverse')
        with pollutant_col3:
            st.metric(label = f"Latest NO2", 
                        value = round([latest_pollutant_data][0]['latest_no2'],1), 
                        delta = round(([latest_pollutant_data][0]['latest_no2'])-([latest_pollutant_data][0]['second_latest_no2']),1),
                        delta_color = 'inverse')
            



    else:
        if parameter_choice == 'PM 2.5':
            parameter_choice = 'pm25'

        st.subheader(f'{renamed_city} {parameter_choice.upper()} (µg/m³):')
        pollutant_col1, pollutant_col2, pollutant_col3 = st.columns(3)
        with pollutant_col1:
            st.metric(label = f"Latest", 
                        value = round([latest_pollutant_data][0][f'latest_{parameter_choice.lower()}'],1), 
                        delta = round(([latest_pollutant_data][0][f'latest_{parameter_choice.lower()}'])-([latest_pollutant_data][0][f'second_latest_{parameter_choice.lower()}']),1),
                        delta_color = 'inverse')
        with pollutant_col2:
            st.metric(label = f"7 day average",
                      value = round(get_av_last_7_days(renamed_city, parameter_choice), 1))
        with pollutant_col3:
            st.metric(label = f"Year average",
                      value = round(get_av_last_year(renamed_city, parameter_choice), 1))  
        

    
#--------------------------------------------------------------------------------------------
# If Global location chosen

else:
    locations_choice = st.selectbox('Choose a location', global_locations)
    country = city_countries.get(locations_choice)
    renamed_city = city_alternate_names.get(locations_choice)
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
        country_selected = st.title(locations_choice.title())
    with flag_col:
        st.image(flag_image, width = 150)

    st.write('')
    st.write('')

    
    parameter_choice = 'pm25'
    latest_pollutant_data = get_latest_pollutants_global(renamed_city)

    st.subheader(f'{renamed_city} PM 2.5 Data (µg/m³):')
    pollutant_col1, pollutant_col2, pollutant_col3 = st.columns(3)
    with pollutant_col1:
        st.metric(label = f"Latest", 
                    value = round([latest_pollutant_data][0]['latest_pm25'],1), 
                    delta = round(([latest_pollutant_data][0]['latest_pm25'])-([latest_pollutant_data][0]['second_latest_pm25']),1),
                    delta_color = 'inverse')
    with pollutant_col2:
        st.metric(label = f"7 day average",
                    value = round(get_av_last_7_days(renamed_city,parameter_choice), 1))
    with pollutant_col3:
        st.metric(label = f"Year average",
                    value = round(get_av_last_year(renamed_city,parameter_choice), 1)) 
    

st.write('')
st.write(' ')
st.write('')
yes_no_comparison = st.radio(f"Compare {locations_choice} with another location?", options = ['Yes','No' ], index = 1)
st.write('')
st.write('')

if yes_no_comparison == 'Yes':
    comparison_choice = st.selectbox(f'Select location to compare with :', all_locations)
    renamed_city_2 = city_alternate_names.get(comparison_choice)
    st.write('')
    st.write('')
    desired_timeframe = st.select_slider('Select Timeframe', options=['Last 24 hours','Last 7 days', 'Last Month', 'Last Year'])
    timeframe = time_frame_to_days.get(desired_timeframe)

    st.write('')
    st.write('')

    if locations_choice in uk_locations and comparison_choice in uk_locations:
        parameter_choice_2 = st.selectbox('Choose parameter to compare', pollution_paramters_2)
        st.write('')
        st.write('')
        compare_cities_pollutant(renamed_city, renamed_city_2, timeframe, parameter_choice_2)
    else:
        parameter_choice_2 = 'pm25'
        compare_cities_pollutant(renamed_city, renamed_city_2, timeframe, parameter_choice_2)
    
    

else:

    desired_timeframe = st.select_slider('Select Timeframe', options=['Last 24 hours','Last 7 days', 'Last Month', 'Last Year'])
    timeframe = time_frame_to_days.get(desired_timeframe)
    st.write('')
    st.write('') 
    if parameter_choice == 'All':
        get_all_pollutants_uk(renamed_city, timeframe)
    else:
        if parameter_choice == 'PM 2.5':
            parameter_choice = 'pm25'
        get_single_pollutant(renamed_city, timeframe, parameter_choice)










