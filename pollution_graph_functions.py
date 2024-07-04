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




######################################################################################
# UK ALL POLLUTANTS - ALL TIMEFRAMES
############################################################################

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

    # SQL query to select data from the chosen timeframe
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

    cur.close()
    conn.close()


    # Converting query result to df
    df = pd.DataFrame(rows, columns=['datetime', f'{renamed_city}_pm25', f'{renamed_city}_o3', f'{renamed_city}_no2'])

    # Convert datetime column to datetime type
    df['datetime'] = pd.to_datetime(df['datetime'])

    # Label font size
    plt.rcParams.update({
        'font.size': 30,
        'axes.titlesize': 30,
        'axes.labelsize': 28,
        'xtick.labelsize': 16,
        'ytick.labelsize': 16,
        'legend.fontsize': 16
    })

    # Using ggplot
    plt.style.use('ggplot')

    # Plotting lines
    plt.figure(figsize=(14, 7))
    plt.plot(df['datetime'], df[f'{renamed_city}_pm25'], label='PM2.5', linestyle='-', color='b', linewidth=1.5, alpha=0.7)
    plt.plot(df['datetime'], df[f'{renamed_city}_o3'], label='O3', linestyle='-', color='g', linewidth=1.5, alpha=0.7)
    plt.plot(df['datetime'], df[f'{renamed_city}_no2'], label='NO2', linestyle='-', color='r', linewidth=1.5, alpha=0.7)

    # Format the date based on timeframe
    if timeframe == 1:
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d %B, %Y %H:%M'))
    elif timeframe == 7 or timeframe == 30:
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d %B, %Y'))
    else:
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%B, %Y'))

    plt.xticks(rotation=30)

    plt.legend()
    plt.xlabel('Date', fontsize=18)
    plt.ylabel('Pollution Level μg/m3', fontsize=18)
    plt.title(f'Pollution Data for {renamed_city}', fontsize=28)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()

    st.pyplot(plt)




#################################################################################################
# ALL SINGLE POLLUTANTS - ANY TIMEFRAME
#################################################################################################

def get_single_pollutant(renamed_city, timeframe, parameter_choice):
    
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
        WHERE {renamed_city}_{parameter_choice.lower()} IS NOT NULL

    """
    cur.execute(latest_datetime_query)
    latest_datetime = cur.fetchone()[0]

    # SQL query to select data from the most recent datetime to 7 days earlier
    sql_query = f"""
        SELECT datetime, {renamed_city}_{parameter_choice.lower()}
        FROM student.bw_air_pollution_data
        WHERE {renamed_city}_pm25 IS NOT NULL
        AND datetime BETWEEN %s AND %s
        AND {renamed_city}_{parameter_choice.lower()} != -999
        ORDER BY datetime
    """

    start_datetime = latest_datetime - timedelta(days= int(f'{timeframe}'))
    cur.execute(sql_query, (start_datetime, latest_datetime))
    rows = cur.fetchall()

    # Close cursor and connection
    cur.close()
    conn.close()

    # Convert query result to a pandas DataFrame
    df = pd.DataFrame(rows, columns=['datetime', f'{renamed_city}_{parameter_choice.lower()}'])

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
    plt.plot(df['datetime'], df[f'{renamed_city}_{parameter_choice.lower()}'], label= f'{parameter_choice.upper()}', linestyle='-', color='b', linewidth=1.5, alpha=0.7)

    # Format the date based on timeframe
    if timeframe == 1:
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d %B, %Y %H:%M'))
    elif timeframe == 7 or timeframe == 30:
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d %B, %Y'))
    else:
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%B, %Y'))

    plt.xticks(rotation=30)

    plt.legend()
    plt.xlabel('Date', fontsize=18)
    plt.ylabel('Pollution Level μg/m3', fontsize=18)
    plt.title(f'{parameter_choice.upper()} Pollution Data for {renamed_city}', fontsize=28)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()

    # Display the plot in Streamlit
    st.pyplot(plt)

##################################################################################################
# COMPARING 2 CITIES FUNCTION

def compare_cities_pollutant(renamed_city, renamed_city_2, timeframe, parameter_choice_2):
    # Establish a connection to the database
    conn = psql.connect(
        dbname=dbname,
        user=username,
        password=password,
        host=host,
        port=port
    )

    # Create a cursor object to execute SQL queries
    cur = conn.cursor()

    # Adjust the parameter_choice_2 for consistency
    if parameter_choice_2 == 'PM 2.5':
        parameter_choice_2 = 'pm25'
    else:
        parameter_choice_2 = parameter_choice_2.lower()

    try:
        # SQL query to get the most recent datetime for the first city
        latest_datetime_query_1 = f"""
            SELECT MAX(datetime)
            FROM student.bw_air_pollution_data
            WHERE {renamed_city}_{parameter_choice_2} IS NOT NULL
        """
        cur.execute(latest_datetime_query_1)
        latest_datetime_1 = cur.fetchone()[0]

        # SQL query to get the most recent datetime for the second city
        latest_datetime_query_2 = f"""
            SELECT MAX(datetime)
            FROM student.bw_air_pollution_data
            WHERE {renamed_city_2}_{parameter_choice_2} IS NOT NULL
        """
        cur.execute(latest_datetime_query_2)
        latest_datetime_2 = cur.fetchone()[0]

        # Use the latest datetime between the two cities
        latest_datetime = min(latest_datetime_1, latest_datetime_2)

        # Calculate the start datetime based on the timeframe
        start_datetime = latest_datetime - timedelta(days=int(timeframe))

        # SQL query to select data for the first city within the specified timeframe
        sql_query_1 = f"""
            SELECT datetime, {renamed_city}_{parameter_choice_2}
            FROM student.bw_air_pollution_data
            WHERE {renamed_city}_{parameter_choice_2} IS NOT NULL
            AND datetime BETWEEN %s AND %s
            AND {renamed_city}_{parameter_choice_2} != -999
            ORDER BY datetime
        """
        cur.execute(sql_query_1, (start_datetime, latest_datetime))
        rows_1 = cur.fetchall()

        # SQL query to select data for the second city within the specified timeframe
        sql_query_2 = f"""
            SELECT datetime, {renamed_city_2}_{parameter_choice_2}
            FROM student.bw_air_pollution_data
            WHERE {renamed_city_2}_{parameter_choice_2} IS NOT NULL
            AND datetime BETWEEN %s AND %s
            AND {renamed_city_2}_{parameter_choice_2} != -999
            ORDER BY datetime
        """
        cur.execute(sql_query_2, (start_datetime, latest_datetime))
        rows_2 = cur.fetchall()

        # Close the cursor and connection to the database
        cur.close()
        conn.close()

        # Convert query results to pandas DataFrames
        df_1 = pd.DataFrame(rows_1, columns=['datetime', f'{renamed_city}_{parameter_choice_2}'])
        df_2 = pd.DataFrame(rows_2, columns=['datetime', f'{renamed_city_2}_{parameter_choice_2}'])

        # Convert datetime column to datetime type
        df_1['datetime'] = pd.to_datetime(df_1['datetime'])
        df_2['datetime'] = pd.to_datetime(df_2['datetime'])

        # Plotting settings
        plt.figure(figsize=(14, 7))
        plt.plot(df_1['datetime'], df_1[f'{renamed_city}_{parameter_choice_2}'], label=f'{parameter_choice_2.upper()} - {renamed_city}', linestyle='-', color='b', linewidth=1.5, alpha=0.7)
        plt.plot(df_2['datetime'], df_2[f'{renamed_city_2}_{parameter_choice_2}'], label=f'{parameter_choice_2.upper()} - {renamed_city_2}', linestyle='-', color='r', linewidth=1.5, alpha=0.7)

        # Format the x-axis based on the timeframe
        if timeframe == 1:
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d %B, %Y %H:%M'))
        elif timeframe == 7 or timeframe == 30:
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d %B, %Y'))
        else:
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%B, %Y'))

        plt.xticks(rotation=30)
        plt.legend()
        plt.xlabel('Date', fontsize=18)
        plt.ylabel('Pollution Level μg/m3', fontsize=18)
        plt.title(f'{parameter_choice_2.upper()} Pollution Data for {renamed_city} and {renamed_city_2}', fontsize=28)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()

        # Display the plot in Streamlit
        st.pyplot(plt)

    except Exception as e:
        st.error(f"Error occurred: {e}")


