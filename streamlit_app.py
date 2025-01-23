import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import psycopg2 as psql
import os
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import plotly.express as px

# import functions from other scripts
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

# Helper function to get flag image URL
def get_flag_url(country_code):
    style = "flat"  # Options: "flat" or "shiny"
    size = "64"  # Options: "64", "128", etc.
    return f"https://flagsapi.com/{country_code}/{style}/{size}.png"

# Location lists
all_locations = ['London Hillingdon',
                     'Oxford', 
                     'Manchester', 
                     'Lima', 
                     'Karachi', 
                     'Singapore' ]

uk_locations = ['London Hillingdon',
                     'Oxford', 
                     'Manchester']

global_locations = [ 'Lima', 
                     'Karachi', 
                     'Singapore' ]

pollution_paramters = ['All','PM 2.5', 'O3', 'NO2']
pollution_paramters_2 = ['PM 2.5', 'O3', 'NO2']

# Dictionaries for location name conversion and date conversion
city_countries = {
    'London Hillingdon': 'united%20kingdom',
    'Oxford': 'united%20kingdom',
    'Manchester': 'united%20kingdom',
    'Lima': 'peru',
    'Karachi': 'pakistan',
    'Singapore': 'singapore'
}

country_codes = {
    'united%20kingdom': 'GB',
    'peru': 'PE',
    'pakistan': 'PK',
    'singapore': 'SG'
}

city_alternate_names = {    
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


# Main header
st.markdown("<h1 style='font-size:48px;'>Open AQ Air Pollution Visualiser</h1>", unsafe_allow_html=True)

st.write('')
st.write('')

# Info dropdown
with st.expander("About this app", expanded=False):
    st.write("""
        This app uses Open AQ to provide air pollution data for various locations in the UK and around the world.
        Select a location to view the latest pollution levels, compare with other locations, 
        and visualize pollution trends over different timeframes.
    """)


# choose UK or Global location 
st.write('')
uk_or_global_choice = st.radio("UK or Global Location?", options = ['UK', 'Global'])
st.write('')
st.write('')

# -----------------------------------------------------------------------------------
# If UK location chosen:

if uk_or_global_choice == 'UK':

    # Location dropdown  
    locations_choice = st.selectbox('Choose a location', uk_locations)
    country = city_countries.get(locations_choice)
    
    # Get the country code for the chosen location
    country_code = country_codes.get(country)
    flag_image_url = get_flag_url(country_code)

    # Displaying location name and flag
    st.write('')
    st.write('')
    name_col, flag_col = st.columns([2, 1])
    with name_col:
        country_selected = st.title(locations_choice.title())
    with flag_col:
        st.image(flag_image_url, width=150)

    st.write('')

    # Pollutant dropdown
    parameter_choice = st.selectbox('Choose pollutant:', pollution_paramters)
    st.write('')
    st.write('')

    # Function called to get latest data
    renamed_city = city_alternate_names.get(locations_choice)
    latest_pollutant_data = get_latest_pollutants_uk(renamed_city, parameter_choice)
    
    if parameter_choice == 'All':
        st.subheader(f'{renamed_city} latest data (\u00b5g/m\u00b3):')
        st.write('')
        
        # Displaying latest data for all pollutants
        pollutant_col1, pollutant_col2, pollutant_col3 = st.columns(3)
        with pollutant_col1:
            st.metric(label="Latest PM 2.5", 
                      value=round([latest_pollutant_data][0]['latest_pm25'], 1), 
                      delta=round(([latest_pollutant_data][0]['latest_pm25'])-([latest_pollutant_data][0]['second_latest_pm25']), 1),
                      delta_color='inverse')
        with pollutant_col2:
            st.metric(label="Latest O3", 
                      value=round([latest_pollutant_data][0]['latest_o3'], 1), 
                      delta=round(([latest_pollutant_data][0]['latest_o3'])-([latest_pollutant_data][0]['second_latest_o3']), 1),
                      delta_color='inverse')
        with pollutant_col3:
            st.metric(label="Latest NO2", 
                      value=round([latest_pollutant_data][0]['latest_no2'], 1), 
                      delta=round(([latest_pollutant_data][0]['latest_no2'])-([latest_pollutant_data][0]['second_latest_no2']), 1),
                      delta_color='inverse')

    else:
        if parameter_choice == 'PM 2.5':
            parameter_choice = 'pm25'

        st.subheader(f'{renamed_city} {parameter_choice.upper()} (\u00b5g/m\u00b3):')

        st.write('')

        # Displaying latest data for PM 2.5 with 7 day and year average
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
    
    # location dropdown
    locations_choice = st.selectbox('Choose a location', global_locations)
    country = city_countries.get(locations_choice)
    renamed_city = city_alternate_names.get(locations_choice)
    latest_pollutant_data = get_latest_pollutants_global(renamed_city)

    # API used for flag image
    country_code = country_codes.get(country)
    flag_image_url = get_flag_url(country_code)

    st.write('')
    st.write('')

    # Displaying location name and flag
    name_col, flag_col = st.columns(2)
    with name_col:
        country_selected = st.title(locations_choice.title())
    with flag_col:
        st.image(flag_image_url, width = 150)

    st.write('')
    st.write('')

    # Getting latest pollutant data for global location
    parameter_choice = 'pm25'
    latest_pollutant_data = get_latest_pollutants_global(renamed_city)

    st.subheader(f'{renamed_city} PM 2.5 Data (\u00b5g/m\u00b3):')

    st.write('')

    # Displaying latest data for PM 2.5 with 7 day and year averag
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

# Comparison yes/no
yes_no_comparison = st.radio(f"Compare {locations_choice} with another location?", options = ['Yes','No' ], index = 1)

st.write('')
st.write(' ')


if yes_no_comparison == 'Yes':

    # Compare location dropdown
    comparison_choice = st.selectbox(f'Select location to compare with :', all_locations)
    renamed_city_2 = city_alternate_names.get(comparison_choice)
    st.write('')
    st.write('')

    # Timeframe selector
    desired_timeframe = st.select_slider('Select Timeframe', options=['Last 24 hours','Last 7 days', 'Last Month', 'Last Year'])
    timeframe = time_frame_to_days.get(desired_timeframe)

    st.write('')
    st.write('')

    # Dropdown if comparing 2 UK cities, else no dropdown (PM 2.5 automatically)
    if locations_choice in uk_locations and comparison_choice in uk_locations:
        parameter_choice_2 = st.selectbox('Choose pollutant to compare:', pollution_paramters_2)
        st.write('')
        st.write('')

        # Plot for pollutant
        compare_cities_pollutant(renamed_city, renamed_city_2, timeframe, parameter_choice_2)
    else:
        parameter_choice_2 = 'pm25'

        # Plot for pollutant
        compare_cities_pollutant(renamed_city, renamed_city_2, timeframe, parameter_choice_2)
    
    

else:

    # Timeframe slider
    desired_timeframe = st.select_slider('Select Timeframe', options=['Last 24 hours','Last 7 days', 'Last Month', 'Last Year'])
    timeframe = time_frame_to_days.get(desired_timeframe)
    st.write('')
    st.write('') 
    st.write(' ')


    if parameter_choice == 'All':

        # Plot for all pollutants
        get_all_pollutants_uk(renamed_city, timeframe)
    else:
        if parameter_choice == 'PM 2.5':
            parameter_choice = 'pm25'
        
        # Plot for single pollutant
        get_single_pollutant(renamed_city, timeframe, parameter_choice)

