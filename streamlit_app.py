import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import psycopg2 as psql
import os
import matplotlib.dates as mdates

from functions import get_all_pollutants_uk
from functions import get_single_pollutant_uk
from functions import get_pollutant_global

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

pollution_paramters = ['All','PM 2.5', 'O3', 'NO2']

st.title("Open AQ Air Pollution Data")

st.write(
    "Use this App to investigate air pollution data for cities across the world!"
)

# choose UK or Global City
uk_or_global_choice = st.radio("UK or Global Location?", options = ['UK', 'Global'])

if uk_or_global_choice == 'UK':
    uk_locations_choice = st.selectbox('Choose a location', uk_locations)
    country = city_countries.get(uk_locations_choice)
    flags_url = f'https://restcountries.com/v3.1/name/{country.lower()}'
    response = requests.get(flags_url)
    flags = response.json()
    flag_image = flags[0]['flags']['png']

# displaying location name and flag
    name_col, flag_col = st.columns(2)
    with name_col:
        country_selected = st.title(uk_locations_choice.title())
    with flag_col:
        st.image(flag_image, width = 150)

    uk_paramater_choice = st.selectbox('Choose pollution parameter', pollution_paramters)
    if uk_paramater_choice == 'All':
        uk_city = city_alternate_names.get(uk_locations_choice)
        get_all_pollutants_uk(uk_city)
    if uk_paramater_choice != 'All':
        uk_city = city_alternate_names.get(uk_locations_choice)
        get_single_pollutant_uk(uk_city, uk_paramater_choice)
    


else:
    global_locations_choice = st.selectbox('Choose a location', global_locations)
    country = city_countries.get(global_locations_choice)
    flags_url = f'https://restcountries.com/v3.1/name/{country.lower()}'
    response = requests.get(flags_url)
    flags = response.json()
    flag_image = flags[0]['flags']['png']

# displaying location name and flag
    name_col, flag_col = st.columns(2)
    with name_col:
        country_selected = st.title(global_locations_choice.title())
    with flag_col:
        st.image(flag_image, width = 150)

    global_city = city_alternate_names.get(global_locations_choice)
    get_pollutant_global(global_city)






























