import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

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

    # Analiza na podstawie typu uszczelki
    seal_types = filtered_df['Seal Type'].unique()
    average_times = {}

    for seal_type in seal_types:
        filtered_type_df = filtered_df[filtered_df['Seal Type'] == seal_type]
        total_time = filtered_type_df['Production Time'].sum()
        total_seals = filtered_type_df['Seal Count'].sum()

        if total_seals > 0:
            avg_time = (total_time / total_seals) * 60  # 🔥 Konwersja na sekundy
            seals_per_minute = 60 / avg_time if avg_time > 0 else 0
            average_times[seal_type] = (avg_time, seals_per_minute)
        else:
            average_times[seal_type] = (None, None)

    st.subheader("📊 By Seal Type")
    result_df = pd.DataFrame(
        [(seal_type, avg[0], avg[1]) for seal_type, avg in average_times.items()],
        columns=['Seal Type', 'Average Time per Seal (seconds)', 'Seals Produced per Minute (UPM)']
    )
    st.table(result_df)

    # Analiza na podstawie firmy
    companies = filtered_df['Company'].unique()
    company_times = {}

    for company in companies:
        filtered_company_df = filtered_df[filtered_df['Company'] == company]
        total_time = filtered_company_df['Production Time'].sum()
        total_seals = filtered_company_df['Seal Count'].sum()

        if total_seals > 0:
            avg_time = (total_time / total_seals) * 60  # 🔥 Konwersja na sekundy
            seals_per_minute = 60 / avg_time if avg_time > 0 else 0
            company_times[company] = (avg_time, seals_per_minute)
        else:
            company_times[company] = (None, None)

    st.subheader("📊 By Company")
    company_df = pd.DataFrame(
        [(company, avg[0], avg[1]) for company, avg in company_times.items()],
        columns=['Company', 'Average Time per Seal (seconds)', 'Seals Produced per Minute (UPM)']
    )
    st.table(company_df)

    # Analiza na podstawie operatora
    operators = filtered_df['Operator'].unique()
    operator_times = {}

    for operator in operators:
        filtered_operator_df = filtered_df[filtered_df['Operator'] == operator]
        total_time = filtered_operator_df['Production Time'].sum()
        total_seals = filtered_operator_df['Seal Count'].sum()

        if total_seals > 0:
            avg_time = (total_time / total_seals) * 60  # 🔥 Konwersja na sekundy
            seals_per_minute = 60 / avg_time if avg_time > 0 else 0
            operator_times[operator] = (avg_time, seals_per_minute)
        else:
            operator_times[operator] = (None, None)

    st.subheader("📊 By Operator")
    operator_df = pd.DataFrame(
        [(operator, avg[0], avg[1]) for operator, avg in operator_times.items()],
        columns=['Operator', 'Average Time per Seal (seconds)', 'Seals Produced per Minute (UPM)']
    )
    st.table(operator_df)
