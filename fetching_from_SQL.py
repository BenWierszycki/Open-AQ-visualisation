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
# Latest pollutant value UK cities

def get_latest_pollutants_uk(renamed_city, pollutant):
    conn = psql.connect(
        database=st.secrets['dbname'],
        user=st.secrets['username'],
        password=st.secrets['password'],
        host=st.secrets['host'],
        port=st.secrets['port']
    )
    cur = conn.cursor()

# Define SQL queries for each pollutant
    pollutants = ['pm25', 'o3', 'no2']
    latest_pollutant_data = {}

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
        latest_value = values[0][0]
        second_latest_value = values[1][0]

        latest_pollutant_data[f"latest_{pollutant}"] = latest_value
        latest_pollutant_data[f"second_latest_{pollutant}"] = second_latest_value

    cur.close()
    conn.close()

    return  latest_pollutant_data

##########################################################################################
# UK last 7 days

def get_av_last_7_days(renamed_city, paramater_choice):
    conn = psql.connect(
        database=st.secrets['dbname'],
        user=st.secrets['username'],
        password=st.secrets['password'],
        host=st.secrets['host'],
        port=st.secrets['port']
        )
    cur = conn.cursor()

    # Define the SQL query to find the latest datetime
    latest_datetime_query = """
        SELECT MAX(datetime)
        FROM student.bw_air_pollution_data"""

    cur.execute(latest_datetime_query)
    latest_datetime = cur.fetchone()[0]

    # Define the SQL query to calculate the average value over the last 7 days
    sql_query = f"""
    SELECT AVG({renamed_city.lower()}_{paramater_choice.lower()})
    FROM student.bw_air_pollution_data
    WHERE datetime BETWEEN %s AND %s
    AND {renamed_city.lower()}_pm25 > -900
    """
    start_datetime = latest_datetime - timedelta(days=7)
    cur.execute(sql_query, (start_datetime, latest_datetime))
    avg_value = cur.fetchone()[0]

    cur.close()
    conn.close()

    return avg_value

####################################################################################
# Uk last year
def get_av_last_year(renamed_city, paramater_choice):
    conn = psql.connect(
        database=st.secrets['dbname'],
        user=st.secrets['username'],
        password=st.secrets['password'],
        host=st.secrets['host'],
        port=st.secrets['port']
        )
    cur = conn.cursor()

    # Define the SQL query to find the latest datetime
    latest_datetime_query = """
        SELECT MAX(datetime)
        FROM student.bw_air_pollution_data"""

    cur.execute(latest_datetime_query)
    latest_datetime = cur.fetchone()[0]

    # Define the SQL query to calculate the average value over the last 7 days
    sql_query = f"""
    SELECT AVG({renamed_city.lower()}_{paramater_choice.lower()})
    FROM student.bw_air_pollution_data
    WHERE datetime BETWEEN %s AND %s
    AND {renamed_city.lower()}_pm25 > -900
    """
    start_datetime = latest_datetime - timedelta(days=365)
    cur.execute(sql_query, (start_datetime, latest_datetime))
    avg_value = cur.fetchone()[0]

    cur.close()
    conn.close()

    return avg_value

########################################################################################

def get_latest_pollutants_global(renamed_city):
    conn = psql.connect(
        database=st.secrets['dbname'],
        user=st.secrets['username'],
        password=st.secrets['password'],
        host=st.secrets['host'],
        port=st.secrets['port']
    )
    cur = conn.cursor()


    sql_query = f"""
        SELECT {renamed_city.lower()}_pm25
        FROM student.bw_air_pollution_data
        WHERE {renamed_city.lower()}_pm25 IS NOT NULL
        AND {renamed_city.lower()}_pm25 > -900
        ORDER BY datetime DESC
        LIMIT 2 """
    
    cur.execute(sql_query)
    values = cur.fetchall()

    latest_value = values[0][0]
    second_latest_value = values[1][0]

    latest_pm25_data = {
        "latest_pm25": latest_value,
        "second_latest_pm25": second_latest_value
    }

    cur.close()
    conn.close()

    return  latest_pm25_data