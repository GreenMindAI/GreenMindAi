import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import requests
from io import StringIO  # Import StringIO from the io module

# Define the raw GitHub file URL
github_raw_url = "https://raw.githubusercontent.com/GreenMindAI/GreenMindAi/main/Retirements78.csv"

# Fetch data from the GitHub URL
response = requests.get(github_raw_url)

# Check if the request was successful
if response.status_code == 200:
    # Load data from the response content using StringIO
    df = pd.read_csv(StringIO(response.text))
    
    # Remove rows with missing or invalid 'Retirement Date' values
    df['Retirement Date'] = pd.to_datetime(df['Retirement Date'], errors='coerce')
    df.dropna(subset=['Retirement Date'], inplace=True)
    
    # Streamlit app title with an emoji
    st.title("🌍 Overall VCM Activity Tracker")
    st.markdown("*The Activity Tracker analyzes the amount of trading activity happening on exchanges and over-the-counter markets. It offers insights into whether carbon credits are being traded more or less often compared to previous months. Users can choose to compare the data over the last 1, 2, 6, or 12 months.*")

    # Rest of your Streamlit app code...
    
    # Get user inputs using Streamlit's text input and selectbox
    retirement_month = st.text_input("Enter the retirement month (e.g., 'August 2023'): ")
    relative_to = st.selectbox("Select the relative time period:", ["1 Month", "3 Months", "6 Months", "1 Year"])
    
    # Convert user input to a timedelta object
    if relative_to == "1 Month":
        delta = timedelta(days=1)
    elif relative_to == "3 Months":
        delta = timedelta(days=1) * 90
    elif relative_to == "6 Months":
        delta = timedelta(days=1) * 180
    elif relative_to == "1 Year":
        delta = timedelta(days=1) * 365
    else:
        st.error("Invalid relative time period input.")
        st.stop()
    
    # Convert retirement_month to a datetime object
    retirement_date = datetime.strptime(retirement_month, '%B %Y')
    
    # Calculate the start and end dates for the specified time period
    start_date = (retirement_date.replace(day=1) - delta).replace(day=1)
    end_date = (retirement_date.replace(day=1) - timedelta(days=1))
    
    # Convert retirement_date to a string in the format 'YYYY-MM' for comparison with DataFrame
    retirement_date_str = retirement_date.strftime('%Y-%m')
    
    # Filter the DataFrame for retirements in the specified time period
    filtered_df = df[df['Retirement Date'].dt.strftime('%Y-%m') == retirement_date_str]
    
    # Calculate the sum of retirements for the specified month and the average for the last N months
    sum_retirements_this_month = filtered_df['Retirements'].sum()
    retirements_last_N_months = df[
        (df['Retirement Date'] >= start_date.strftime('%Y-%m-%d')) &
        (df['Retirement Date'] < retirement_date.strftime('%Y-%m-%d'))
    ]['Retirements'].sum()
    number_of_months = len(pd.date_range(start_date, end_date, freq='M'))
    average_retirements_last_N_months = int(retirements_last_N_months / number_of_months)
    
    # Compare the results and display using Streamlit
    st.write("Retirement Month:", retirement_month)
    st.write("Relative To:", relative_to)
    st.write("Start Date:", start_date)
    st.write("End Date:", end_date)
    st.write("Sum of Retirements for the Specified Month:", f"**{sum_retirements_this_month:,.0f}**")
    st.write(f"Average of Retirements for the Last {number_of_months} Months:", f"**{average_retirements_last_N_months:,.0f}**")
    
    if sum_retirements_this_month > average_retirements_last_N_months:
        difference = ((sum_retirements_this_month - average_retirements_last_N_months) / average_retirements_last_N_months) * 100
        st.write(f"Retirements rose by {difference:.2f}% relative to the average of the last {relative_to}.")
    elif sum_retirements_this_month < average_retirements_last_N_months:
        difference = ((average_retirements_last_N_months - sum_retirements_this_month) / average_retirements_last_N_months) * 100
        st.write(f"Retirements decreased by {difference:.2f}% relative to the average of the last {relative_to}.")
    else:
        st.write(f"Retirements remained the same relative to the average of the last {relative_to}.")
else:
    st.error("Failed to retrieve data from GitHub. Please check the URL and try again.")


