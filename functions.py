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



###########################################################################################
# SINGLE POLLUTANT UK


##############################################################################################
# SINGLE POLLUTANT GLOBAL

def get_pollutant_global(renamed_city):
            
    conn = psql.connect(
        dbname=dbname,
        user=username,
        password=password,
        host=host,
        port=port
    )

    cur = conn.cursor()

    # SQL query to select data
    sql_query = f"""
        SELECT datetime, {renamed_city}_pm25
        FROM student.bw_air_pollution_data
        WHERE {renamed_city}_pm25 IS NOT NULL 
        AND {renamed_city}_pm25 != -999
        ORDER BY datetime
    """

    cur.execute(sql_query)
    rows = cur.fetchall()

    # Close cursor and connection
    cur.close()
    conn.close()

    # Convert query result to a pandas DataFrame
    df = pd.DataFrame(rows, columns=['datetime', f'{renamed_city}_pm25'])

    # Convert datetime column to datetime type
    df['datetime'] = pd.to_datetime(df['datetime'])

    # Setting the font size for labels
    plt.rcParams.update({
        'font.size': 30,
        'axes.titlesize': 30,
        'axes.labelsize': 28,
        'xtick.labelsize': 16,
        'ytick.labelsize': 16,
        'legend.fontsize': 16
    })

    # Using ggplot style
    plt.style.use('ggplot')

    # Plotting with matplotlib
    plt.figure(figsize=(14, 7))
    plt.plot(df['datetime'], df[f'{renamed_city}_pm25'], label='PM2.5', linestyle='-', color='b', linewidth=1.5, alpha=0.7)

    # Format the date to MM-YYYY
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%Y'))

    plt.xticks(rotation=45)

    plt.legend()
    plt.xlabel('Date', fontsize = 18)
    plt.ylabel('Pollution Level μg/m3', fontsize = 18)
    plt.title(f'PM2.5 Pollution Data for {renamed_city}', fontsize = 28)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()

    # Display the plot in Streamlit
    return st.pyplot(plt)

######################################################################################
# UK ALL POLLUTANTS - ALL TIMEFRAMES

def get_all_pollutants_uk(renamed_city, timeframe):
    
    conn = psql.connect(
        dbname=dbname,
        user=username,
        password=password,
        host=host,
        port=port
    )

    cur = conn.cursor()

    # SQL query to get the most recent datetime
    latest_datetime_query = f"""
        SELECT MAX(datetime)
        FROM student.bw_air_pollution_data
        WHERE {renamed_city}_pm25 IS NOT NULL
    """
    cur.execute(latest_datetime_query)
    latest_datetime = cur.fetchone()[0]

    # SQL query to select data from the most recent datetime to 7 days earlier
    sql_query = f"""
        SELECT datetime, {renamed_city}_pm25, {renamed_city}_o3, {renamed_city}_no2
        FROM student.bw_air_pollution_data
        WHERE {renamed_city}_pm25 IS NOT NULL
        AND {renamed_city}_NO2 < 200
        AND datetime BETWEEN %s AND %s
        ORDER BY datetime
    """

    start_datetime = latest_datetime - timedelta(days= int(f'{timeframe}'))
    cur.execute(sql_query, (start_datetime, latest_datetime))
    rows = cur.fetchall()

    # Close cursor and connection
    cur.close()
    conn.close()

    # Convert query result to a pandas DataFrame
    df = pd.DataFrame(rows, columns=['datetime', f'{renamed_city}_pm25', f'{renamed_city}_o3', f'{renamed_city}_no2'])

    # Convert datetime column to datetime type
    df['datetime'] = pd.to_datetime(df['datetime'])

    # Setting the font size for labels
    plt.rcParams.update({
        'font.size': 30,
        'axes.titlesize': 30,
        'axes.labelsize': 28,
        'xtick.labelsize': 16,
        'ytick.labelsize': 16,
        'legend.fontsize': 16
    })

    # Using ggplot style
    plt.style.use('ggplot')

    # Plotting with matplotlib
    plt.figure(figsize=(14, 7))
    plt.plot(df['datetime'], df[f'{renamed_city}_pm25'], label='PM2.5', linestyle='-', color='r', linewidth=1.5, alpha=0.7)
    plt.plot(df['datetime'], df[f'{renamed_city}_o3'], label='O3', linestyle='-', color='g', linewidth=1.5, alpha=0.7)
    plt.plot(df['datetime'], df[f'{renamed_city}_no2'], label='NO2', linestyle='-', color='b', linewidth=1.5, alpha=0.7)

    # Format the date to MM-YYYY
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y %H:%M'))

    plt.xticks(rotation=30)

    plt.legend()
    plt.xlabel('Date', fontsize=18)
    plt.ylabel('Pollution Level μg/m3', fontsize=18)
    plt.title(f'Pollution Data for {renamed_city}', fontsize=28)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()

    # Display the plot in Streamlit
    st.pyplot(plt)

#################################################################################################
# UK SINGLE POLLUTANTS - 1 MONTH

def get_single_pollutant(renamed_city, timeframe, paramater_choice):
    
    conn = psql.connect(
        dbname=dbname,
        user=username,
        password=password,
        host=host,
        port=port
    )

    cur = conn.cursor()

    # SQL query to get the most recent datetime
    latest_datetime_query = f"""
        SELECT MAX(datetime)
        FROM student.bw_air_pollution_data
        WHERE {renamed_city}_{paramater_choice.lower()} IS NOT NULL

    """
    cur.execute(latest_datetime_query)
    latest_datetime = cur.fetchone()[0]

    # SQL query to select data from the most recent datetime to 7 days earlier
    sql_query = f"""
        SELECT datetime, {renamed_city}_{paramater_choice.lower()}
        FROM student.bw_air_pollution_data
        WHERE {renamed_city}_pm25 IS NOT NULL
        AND datetime BETWEEN %s AND %s
        AND {renamed_city}_{paramater_choice.lower()} != -999
        ORDER BY datetime
    """

    start_datetime = latest_datetime - timedelta(days= int(f'{timeframe}'))
    cur.execute(sql_query, (start_datetime, latest_datetime))
    rows = cur.fetchall()

    # Close cursor and connection
    cur.close()
    conn.close()

    # Convert query result to a pandas DataFrame
    df = pd.DataFrame(rows, columns=['datetime', f'{renamed_city}_{paramater_choice.lower()}'])

    # Convert datetime column to datetime type
    df['datetime'] = pd.to_datetime(df['datetime'])

    # Setting the font size for labels
    plt.rcParams.update({
        'font.size': 30,
        'axes.titlesize': 30,
        'axes.labelsize': 28,
        'xtick.labelsize': 16,
        'ytick.labelsize': 16,
        'legend.fontsize': 16
    })

    # Using ggplot style
    plt.style.use('ggplot')

    # Plotting with matplotlib
    plt.figure(figsize=(14, 7))
    plt.plot(df['datetime'], df[f'{renamed_city}_{paramater_choice.lower()}'], label= f'{paramater_choice.upper()}', linestyle='-', color='b', linewidth=1.5, alpha=0.7)

    # Format the date to MM-YYYY
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y %H:%M'))

    plt.xticks(rotation=30)

    plt.legend()
    plt.xlabel('Date', fontsize=18)
    plt.ylabel('Pollution Level μg/m3', fontsize=18)
    plt.title(f'{paramater_choice.upper()} Pollution Data for {renamed_city}', fontsize=28)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()

    # Display the plot in Streamlit
    st.pyplot(plt)


