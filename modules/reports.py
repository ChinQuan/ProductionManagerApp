import pandas as pd
import streamlit as st
from datetime import datetime

def show_reports(df):
    st.header("📊 Reports")

    if df.empty:
        st.write("No data available.")
        return

    # ✅ Konwersja kolumny 'Date' do formatu datetime
    try:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    except Exception as e:
        st.error(f"❌ Error converting dates: {e}")
        return

    # 📅 Filtr daty
    start_date = st.sidebar.date_input("Start Date", value=datetime.now() - pd.DateOffset(days=30))
    end_date = st.sidebar.date_input("End Date", value=datetime.now())

    # ✅ Filtrujemy dane na podstawie przedziału dat
    filtered_df = df[(df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))]

    if filtered_df.empty:
        st.write("No data available for the selected date range.")
        return

    # 🔍 Wybór typu filtrowania
    filter_option = st.selectbox(
        "Select Data Filter",
        ["All Data", "Working Days Only (Mon-Fri)", "Order Dates Only"]
    )

    if filter_option == "Working Days Only (Mon-Fri)":
        filtered_df = filtered_df[filtered_df['Date'].dt.dayofweek < 5]

    elif filter_option == "Order Dates Only":
        filtered_df = filtered_df.dropna(subset=['Date'])

    if filtered_df.empty:
        st.write("No data available after applying the filter.")
        return

    st.subheader("Filtered Data")
    st.dataframe(filtered_df)

    # 📊 Przykładowy raport - Suma uszczelek na firmę
    seals_per_company = filtered_df.groupby('Company')['Seal Count'].sum().sort_values(ascending=False)
    st.subheader("Total Seals Produced by Company")
    st.bar_chart(seals_per_company)

    # 📊 Przykładowy raport - Suma uszczelek na operatora
    seals_per_operator = filtered_df.groupby('Operator')['Seal Count'].sum().sort_values(ascending=False)
    st.subheader("Total Seals Produced by Operator")
    st.bar_chart(seals_per_operator)

    # 📊 Przykładowy raport - Suma uszczelek na typ uszczelki
    seals_per_type = filtered_df.groupby('Seal Type')['Seal Count'].sum().sort_values(ascending=False)
    st.subheader("Total Seals Produced by Seal Type")
    st.bar_chart(seals_per_type)
