import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import psycopg2 as psql
import os
import matplotlib.dates as mdates

username = st.secrets['username']
password = st.secrets['password']
host = st.secrets['host']
dbname = st.secrets['dbname']
port = st.secrets['port']

def get_all_pollutants_uk(uk_city):
            
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
            SELECT datetime, {uk_city}_pm25, {uk_city}_o3, {uk_city}_no2
            FROM student.bw_air_pollution_data
            WHERE {uk_city}_pm25 IS NOT NULL
            AND {uk_city}_NO2 < 200
            ORDER BY datetime
        """

        cur.execute(sql_query)
        rows = cur.fetchall()

        # Close cursor and connection
        cur.close()
        conn.close()

        # Convert query result to a pandas DataFrame
        df = pd.DataFrame(rows, columns=['datetime', f'{uk_city}_pm25', f'{uk_city}_o3', f'{uk_city}_no2'])

        # Convert datetime column to datetime type
        df['datetime'] = pd.to_datetime(df['datetime'])

        # Setting the font size for labels
        plt.rcParams.update({
            'font.size': 14,
            'axes.titlesize': 20,
            'axes.labelsize': 18,
            'xtick.labelsize': 14,
            'ytick.labelsize': 14,
            'legend.fontsize': 16
        })
        
        # Plotting with matplotlib
        plt.figure(figsize=(12, 6))
        plt.plot(df['datetime'], df[f'{uk_city}_pm25'], label='PM2.5', linestyle='-', color='r', linewidth=0.75)
        plt.plot(df['datetime'], df[f'{uk_city}_o3'], label='O3', linestyle='-', color='g', linewidth=0.75)
        plt.plot(df['datetime'], df[f'{uk_city}_no2'], label='NO2', linestyle='-', color='b', linewidth=0.75)

        # Format the date to MM-YYYY
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%Y'))

        plt.legend()
        plt.xlabel('Date')
        plt.ylabel('Pollution Level μg/m3')
        plt.title(f'Pollution Data for {uk_city}')
        plt.tight_layout()

        # Display the plot in Streamlit
        return st.pyplot(plt)

###########################################################################################

def get_single_pollutant_uk(uk_city, uk_paramater_choice):
            
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
            SELECT datetime, {uk_city}_{uk_paramater_choice.lower()}
            FROM student.bw_air_pollution_data
            WHERE {uk_city}_{uk_paramater_choice.lower()} IS NOT NULL
            AND {uk_city}_{uk_paramater_choice.lower()} < 200
            ORDER BY datetime
        """

        cur.execute(sql_query)
        rows = cur.fetchall()

        # Close cursor and connection
        cur.close()
        conn.close()

        # Convert query result to a pandas DataFrame
        df = pd.DataFrame(rows, columns=['datetime', f'{uk_city}_{uk_paramater_choice.lower()}'])

        # Convert datetime column to datetime type
        df['datetime'] = pd.to_datetime(df['datetime'])

        # Setting the font size for labels
        plt.rcParams.update({
            'font.size': 14,
            'axes.titlesize': 20,
            'axes.labelsize': 18,
            'xtick.labelsize': 14,
            'ytick.labelsize': 14,
            'legend.fontsize': 16
        })

        # Plotting with matplotlib
        plt.figure(figsize=(12, 6))
        plt.plot(df['datetime'], df[f'{uk_city}_{uk_paramater_choice.lower()}'], label=f'{uk_paramater_choice}', linestyle='-', color='b', linewidth=0.75)

        # Format the date to MM-YYYY
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%Y'))

        plt.legend()
        plt.xlabel('Date')
        plt.ylabel('Pollution Level μg/m3')
        plt.title(f'{uk_paramater_choice.upper()} Pollution Data for {uk_city}')
        plt.tight_layout()

        # Display the plot in Streamlit
        return st.pyplot(plt)

##############################################################################################

def get_pollutant_global(global_city):
            
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
            SELECT datetime, {global_city}_pm25
            FROM student.bw_air_pollution_data
            WHERE {global_city}_pm25 IS NOT NULL 
            AND {global_city}_pm25 != -999
            ORDER BY datetime
        """

        cur.execute(sql_query)
        rows = cur.fetchall()

        # Close cursor and connection
        cur.close()
        conn.close()

        # Convert query result to a pandas DataFrame
        df = pd.DataFrame(rows, columns=['datetime', f'{global_city}_pm25'])

        # Convert datetime column to datetime type
        df['datetime'] = pd.to_datetime(df['datetime'])

    # Setting the font size for labels
        plt.rcParams.update({
            'font.size': 14,
            'axes.titlesize': 20,
            'axes.labelsize': 18,
            'xtick.labelsize': 14,
            'ytick.labelsize': 14,
            'legend.fontsize': 16
        })

        # Plotting with matplotlib
        plt.figure(figsize=(12, 6))
        plt.plot(df['datetime'], df[f'{global_city}_pm25'], label='PM2.5', linestyle='-', color='b', linewidth=0.75)

        # Format the date to MM-YYYY
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%Y'))

        plt.legend()
        plt.xlabel('Date')
        plt.ylabel('Pollution Level μg/m3')
        plt.title(f'PM2.5 Pollution Data for {global_city}')
        plt.tight_layout()

        # Display the plot in Streamlit
        return st.pyplot(plt)



