import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import psycopg2 as psql
import os
import matplotlib.dates as mdates
import seaborn
from datetime import datetime, timedelta
import plotly.express as px

username = st.secrets['username']
password = st.secrets['password']
host = st.secrets['host']
dbname = st.secrets['dbname']
port = st.secrets['port']


##########################################################################
# Function plotting UK pollution data - all 3 pollutants


@st.cache_data
def get_all_pollutants_uk(renamed_city, timeframe):
    
    conn = psql.connect(
        dbname=dbname,
        user=username,
        password=password,
        host=host,
        port=port
    )

    cur = conn.cursor()

    # Get most recent datetime
    latest_datetime_query = f"""
        SELECT MAX(datetime)
        FROM student.bw_air_pollution_data
        WHERE {renamed_city}_pm25 IS NOT NULL
    """
    cur.execute(latest_datetime_query)
    latest_datetime = cur.fetchone()[0]

    # Select data from the chosen timeframe
    sql_query = f"""
        SELECT datetime, {renamed_city}_pm25, {renamed_city}_o3, {renamed_city}_no2
        FROM student.bw_air_pollution_data
        WHERE {renamed_city}_pm25 IS NOT NULL
        AND {renamed_city}_NO2 < 200
        AND datetime BETWEEN %s AND %s
        ORDER BY datetime
    """

    # Calculate start date
    start_datetime = latest_datetime - timedelta(days=int(timeframe))
    cur.execute(sql_query, (start_datetime, latest_datetime))
    rows = cur.fetchall()

    cur.close()
    conn.close()

    # Convert query result to df
    df = pd.DataFrame(rows, columns=['datetime', f'{renamed_city}_pm25', f'{renamed_city}_o3', f'{renamed_city}_no2'])

    # Make datetime column datetime type
    df['datetime'] = pd.to_datetime(df['datetime'])

    # Combine pollution columns for plotting
    df_melted = df.melt(id_vars='datetime', var_name='Pollutant', value_name='Value')

    # Remove city name from pollutant names
    df_melted['Pollutant'] = df_melted['Pollutant'].str.replace(f'{renamed_city}_', '').str.upper()

    # Plotly interactive line
    fig = px.line(
        df_melted,
        x='datetime',
        y='Value',
        color='Pollutant',
        title=f'Pollution Data for {renamed_city}',
        labels={'datetime': 'Date', 'Value': 'Pollution Level μg/m3', 'Pollutant': 'Pollutant'},
    )

    # Layout and date formatting
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Pollution Level μg/m3',
        title_font_size=28,
        xaxis=dict(
            tickformat='%d %B, %Y %H:%M' if timeframe == 1 else '%d %B, %Y' if timeframe in [7, 30] else '%B, %Y',
            tickangle=30,
        ),
        legend_title='Pollutant'
    )

    # Update hover information
    fig.update_traces(
        hovertemplate='Date = %{x}<br>Pollutant = %{fullData.name}<br>Value = %{y:.2f}'
    )

    st.plotly_chart(fig)

###########################################################################################################
# Function plotting single pollutant data - all locations


@st.cache_data
def get_single_pollutant(renamed_city, timeframe, parameter_choice):
    conn = psql.connect(
        dbname=st.secrets['dbname'],
        user=st.secrets['username'],
        password=st.secrets['password'],
        host=st.secrets['host'],
        port=st.secrets['port']
    )

    cur = conn.cursor()

    # Get most recent datetime
    latest_datetime_query = f"""
        SELECT MAX(datetime)
        FROM student.bw_air_pollution_data
        WHERE {renamed_city}_{parameter_choice.lower()} IS NOT NULL
    """
    cur.execute(latest_datetime_query)
    latest_datetime = cur.fetchone()[0]

    # Select data from the chosen timeframe
    sql_query = f"""
        SELECT datetime, {renamed_city}_{parameter_choice.lower()}
        FROM student.bw_air_pollution_data
        WHERE {renamed_city}_pm25 IS NOT NULL
        AND datetime BETWEEN %s AND %s
        AND {renamed_city}_{parameter_choice.lower()} != -999
        ORDER BY datetime
    """

    # Calculate start date
    start_datetime = latest_datetime - timedelta(days=int(timeframe))
    cur.execute(sql_query, (start_datetime, latest_datetime))
    rows = cur.fetchall()

    cur.close()
    conn.close()

    # Convert query result to df
    df = pd.DataFrame(rows, columns=['datetime', f'{renamed_city}_{parameter_choice.lower()}'])

    # Make datetime column datetime type
    df['datetime'] = pd.to_datetime(df['datetime'])

    # Combine pollution columns for plotting
    df_melted = df.melt(id_vars='datetime', var_name='Pollutant', value_name='Value')

    # Remove city name from pollutant names
    df_melted['Pollutant'] = df_melted['Pollutant'].str.replace(f'{renamed_city}_', '').str.upper()

    # Plotly interactive line
    fig = px.line(
        df_melted,
        x='datetime',
        y='Value',
        color='Pollutant',
        title=f'{parameter_choice.upper()} Pollution Data for {renamed_city}',
        labels={'datetime': 'Date', 'Value': 'Pollution Level μg/m³', 'Pollutant': 'Pollutant'},
    )

    # Update hover information
    fig.update_traces(hovertemplate='<br>'.join([
        'Date = %{x|%d %B, %Y %H:%M}',
        'Pollutant = %{fullData.name}',
        'Value = %{y:.2f}'
    ]))

    # Layout and date formatting
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Pollution Level μg/m³',
        title_font_size=28,
        xaxis=dict(
            tickformat='%d %B, %Y %H:%M' if timeframe == 1 else '%d %B, %Y' if timeframe in [7, 30] else '%B, %Y',
            tickangle=30,
        ),
        legend_title='Pollutant'
    )

    st.plotly_chart(fig)


###########################################################################################################
# Function comparing single pollutant data across locations


@st.cache_data
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

    # Get most recent datetime for location 1
    latest_datetime_query_1 = f"""
        SELECT MAX(datetime)
        FROM student.bw_air_pollution_data
        WHERE {renamed_city}_{parameter_choice_2} IS NOT NULL
    """
    cur.execute(latest_datetime_query_1)
    latest_datetime_1 = cur.fetchone()[0]

    # Get most recent datetime for location 2
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

    # Select data from the chosen timeframe
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

    # Convert query results to dfs
    df_1 = pd.DataFrame(rows_1, columns=['datetime', f'{renamed_city}_{parameter_choice_2}'])
    df_2 = pd.DataFrame(rows_2, columns=['datetime', f'{renamed_city_2}_{parameter_choice_2}'])

    # Make datetime column datetime type
    df_1['datetime'] = pd.to_datetime(df_1['datetime'])
    df_2['datetime'] = pd.to_datetime(df_2['datetime'])

    # Merge dataframes for easier plotting with Plotly
    df_1 = df_1.rename(columns={f'{renamed_city}_{parameter_choice_2}': f'{renamed_city}'})
    df_2 = df_2.rename(columns={f'{renamed_city_2}_{parameter_choice_2}': f'{renamed_city_2}'})

    df_combined = pd.merge(df_1, df_2, on='datetime', how='outer')

    # Combine pollution columns for plotting
    df_melted = df_combined.melt(id_vars='datetime', var_name='Location', value_name='Value')

    # Plotly interactive line
    fig = px.line(
        df_melted,
        x='datetime',
        y='Value',
        color='Location',
        title=f'{parameter_choice_2.upper()} Pollution Data for {renamed_city} and {renamed_city_2}',
        labels={'datetime': 'Date', 'Value': 'Pollution Level μg/m3', 'Location': 'Location'},
    )

    # Layout and date formatting
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Pollution Level μg/m3',
        title_font_size=28,
        xaxis=dict(
            tickformat='%d %B, %Y %H:%M' if timeframe == 1 else '%d %B, %Y' if timeframe in [7, 30] else '%B, %Y',
            tickangle=30,
        ),
        legend_title='Location'
    )

    # Update hover information
    fig.update_traces(
        hovertemplate='Date = %{x}<br>Location = %{fullData.name}<br>Value = %{y:.2f}'
    )

    st.plotly_chart(fig)






