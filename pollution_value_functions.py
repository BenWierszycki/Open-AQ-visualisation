import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import psycopg2 as psql
import os
import matplotlib.dates as mdates
import seaborn
from datetime import datetime, timedelta

username = st.secrets['username']
password = st.secrets['password']
host = st.secrets['host']
dbname = st.secrets['dbname']
port = st.secrets['port']

####################################################################################
# Function for latest pollutant value - UK cities

@st.cache_data
def get_latest_pollutants_uk(renamed_city, pollutant):
    conn = psql.connect(
        database=st.secrets['dbname'],
        user=st.secrets['username'],
        password=st.secrets['password'],
        host=st.secrets['host'],
        port=st.secrets['port']
    )
    cur = conn.cursor()

    # Queries for each pollutant
    pollutants = ['pm25', 'o3', 'no2']
    latest_pollutant_data = {}

    # Query retrieving latest 2 data readings
    for pollutant in pollutants:
        sql_query = f"""
            SELECT {renamed_city.lower()}_{pollutant.lower()}
            FROM student.bw_air_pollution_data
            WHERE {renamed_city.lower()}_{pollutant.lower()} IS NOT NULL
            ORDER BY datetime DESC
            LIMIT 2
        """
        cur.execute(sql_query)
        values = cur.fetchall()

        # Handling cases with no data
        if len(values) == 0:
            latest_value = 0  # No data available, default to 0
            second_latest_value = 0
        elif len(values) == 1:
            latest_value = values[0][0]  # Only one value available
            second_latest_value = 0
        else:
            # Two or more values available
            latest_value = values[0][0]
            second_latest_value = values[1][0]

        latest_pollutant_data[f"latest_{pollutant}"] = latest_value
        latest_pollutant_data[f"second_latest_{pollutant}"] = second_latest_value

    cur.close()
    conn.close()

    return latest_pollutant_data


##########################################################################################
# Function for last 7 day average 

@st.cache_data
def get_av_last_7_days(renamed_city, parameter_choice):
    conn = psql.connect(
        database=st.secrets['dbname'],
        user=st.secrets['username'],
        password=st.secrets['password'],
        host=st.secrets['host'],
        port=st.secrets['port']
    )
    cur = conn.cursor()

    # Getting the latest datetime
    latest_datetime_query = """
        SELECT MAX(datetime)
        FROM student.bw_air_pollution_data"""
    cur.execute(latest_datetime_query)
    latest_datetime = cur.fetchone()[0]

    # Calculating the average value over the last 7 days
    sql_query = f"""
    SELECT AVG({renamed_city.lower()}_{parameter_choice.lower()})
    FROM student.bw_air_pollution_data
    WHERE datetime BETWEEN %s AND %s
    AND {renamed_city.lower()}_{parameter_choice.lower()} > -900
    """
    start_datetime = latest_datetime - timedelta(days=7)
    cur.execute(sql_query, (start_datetime, latest_datetime))
    avg_value = cur.fetchone()[0]

    # If no data exists in the timeframe, fetch the latest value
    if avg_value is None:
        fallback_query = f"""
        SELECT {renamed_city.lower()}_{parameter_choice.lower()}
        FROM student.bw_air_pollution_data
        WHERE {renamed_city.lower()}_{parameter_choice.lower()} IS NOT NULL
        AND {renamed_city.lower()}_{parameter_choice.lower()} > -900
        ORDER BY datetime DESC
        LIMIT 1
        """
        cur.execute(fallback_query)
        avg_value = cur.fetchone()[0]  # Use the latest value as a fallback

    cur.close()
    conn.close()

    return avg_value

####################################################################################
# Function for last year average

@st.cache_data
def get_av_last_year(renamed_city, parameter_choice):
    conn = psql.connect(
        database=st.secrets['dbname'],
        user=st.secrets['username'],
        password=st.secrets['password'],
        host=st.secrets['host'],
        port=st.secrets['port']
    )
    cur = conn.cursor()

    # Getting the latest datetime
    latest_datetime_query = """
        SELECT MAX(datetime)
        FROM student.bw_air_pollution_data"""
    cur.execute(latest_datetime_query)
    latest_datetime = cur.fetchone()[0]

    # Calculating the average value over the last year
    sql_query = f"""
    SELECT AVG({renamed_city.lower()}_{parameter_choice.lower()})
    FROM student.bw_air_pollution_data
    WHERE datetime BETWEEN %s AND %s
    AND {renamed_city.lower()}_{parameter_choice.lower()} > -900
    """
    start_datetime = latest_datetime - timedelta(days=365)
    cur.execute(sql_query, (start_datetime, latest_datetime))
    avg_value = cur.fetchone()[0]

    # If no data exists in the timeframe, fetch the latest value
    if avg_value is None:
        fallback_query = f"""
        SELECT {renamed_city.lower()}_{parameter_choice.lower()}
        FROM student.bw_air_pollution_data
        WHERE {renamed_city.lower()}_{parameter_choice.lower()} IS NOT NULL
        AND {renamed_city.lower()}_{parameter_choice.lower()} > -900
        ORDER BY datetime DESC
        LIMIT 1
        """
        cur.execute(fallback_query)
        avg_value = cur.fetchone()[0]  # Use the latest value as a fallback

    cur.close()
    conn.close()

    return avg_value

########################################################################################
# Function for latest pollutant value - Global cities

@st.cache_data
def get_latest_pollutants_global(renamed_city):
    conn = psql.connect(
        database=st.secrets['dbname'],
        user=st.secrets['username'],
        password=st.secrets['password'],
        host=st.secrets['host'],
        port=st.secrets['port']
    )
    cur = conn.cursor()

    # Query retrieving latest 2 data readings
    sql_query = f"""
        SELECT {renamed_city.lower()}_pm25
        FROM student.bw_air_pollution_data
        WHERE {renamed_city.lower()}_pm25 IS NOT NULL
        AND {renamed_city.lower()}_pm25 > -900
        ORDER BY datetime DESC
        LIMIT 2 """
    
    cur.execute(sql_query)
    values = cur.fetchall()

    # Defining latest and 2nd latest value
    latest_value = values[0][0]
    second_latest_value = values[1][0]

    latest_pm25_data = {
        "latest_pm25": latest_value,
        "second_latest_pm25": second_latest_value
    }

    cur.close()
    conn.close()

    return  latest_pm25_data
