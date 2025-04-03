import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def format_time(seconds):
    if seconds < 60:
        return f"{int(seconds)} seconds"
    else:
        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)
        return f"{minutes} minute{'s' if minutes > 1 else ''} {remaining_seconds} seconds"

def calculate_average_time(df):
    st.header("⏳ Average Production Time Analysis")

    if df.empty:
        st.write("No data available to calculate average production time.")
        return

    if 'Date' not in df.columns:
        st.write("Date column not found in data.")
        return

    # Konwersja kolumny 'Date' do formatu datetime
    df['Date'] = pd.to_datetime(df['Date'])

    # 📅 Opcje wyboru przedziału czasowego
    st.sidebar.header("📅 Filter by Date Range")
    date_filter = st.sidebar.selectbox(
        "Select Date Range",
        ["Last Week", "Last Month", "Last Year", "Custom Range"]
    )

    if date_filter == "Last Week":
        start_date = datetime.now() - timedelta(weeks=1)
        end_date = datetime.now()
    elif date_filter == "Last Month":
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
    elif date_filter == "Last Year":
        start_date = datetime.now() - timedelta(days=365)
        end_date = datetime.now()
    else:
        start_date = st.sidebar.date_input("Start Date", value=datetime.now() - timedelta(days=30))
        end_date = st.sidebar.date_input("End Date", value=datetime.now())
    
    # Filtrujemy dane na podstawie wybranego przedziału czasowego
    filtered_df = df[(df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))]

    if filtered_df.empty:
        st.write("No data available for the selected date range.")
        return

    st.write(f"Showing data from **{start_date.date()}** to **{end_date.date()}**")

    # 📌 Stylizacja tabeli CSS dla wyśrodkowania
    st.markdown(
        """
        <style>
        table td, table th {
            text-align: center !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Analiza na podstawie typu uszczelki
    seal_types = filtered_df['Seal Type'].unique()
    average_times = {}

    for seal_type in seal_types:
        filtered_type_df = filtered_df
