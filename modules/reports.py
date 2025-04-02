import streamlit as st
import pandas as pd
from datetime import datetime

def show_reports(df):
    st.header("📊 Reports")
    
    if df.empty:
        st.write("No data available to generate reports.")
        return

    # Filtrowanie danych po dacie
    start_date = st.date_input("Start Date", value=datetime.now())
    end_date = st.date_input("End Date", value=datetime.now())

    if start_date > end_date:
        st.warning("Start date cannot be after end date.")
        return

    filtered_df = df[(pd.to_datetime(df['Date']) >= pd.to_datetime(start_date)) & (pd.to_datetime(df['Date']) <= pd.to_datetime(end_date))]

    if filtered_df.empty:
        st.write("No data found for the selected period.")
        return

    # Najlepszy operator
    top_operator = filtered_df.groupby('Operator')['Seal Count'].sum().idxmax()
    st.write(f"Top Operator: {top_operator}")

    # Najbardziej produktywna firma
    top_company = filtered_df.groupby('Company')['Seal Count'].sum().idxmax()
    st.write(f"Top Company: {top_company}")

    # Eksport danych do CSV
    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Report as CSV", data=csv_data, file_name="report.csv", mime="text/csv")
