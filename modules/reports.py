import pandas as pd
import streamlit as st
from datetime import datetime, date

def show_reports(df):
    st.header("📊 Reports")

    if df.empty:
        st.write("No data available.")
        return

    # ✅ Konwersja kolumny 'Date' do formatu datetime.date (tylko data, bez godzin)
    try:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.date  # 🔥 Usunięcie godziny, pozostaje tylko data
        st.write("📅 Debug: DataFrame after converting 'Date' column (Date Only)")
        st.dataframe(df.head(10))
    except Exception as e:
        st.error(f"❌ Error converting dates: {e}")
        return

    # 📅 Filtr daty - wybór przedziału czasowego
    start_date = st.sidebar.date_input("Start Date", value=(datetime.now().date() - pd.DateOffset(days=30)).date(), key="start_date")
    end_date = st.sidebar.date_input("End Date", value=datetime.now().date(), key="end_date")

    # ✅ Pokaż pełne dane przed filtracją (to będą dane używane w raportach)
    st.write("📅 Debug: Full DataFrame before date filtering")
    st.dataframe(df)

    # ✅ Filtrujemy dane na podstawie wybranego przedziału dat
    filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]  # 🔥 Porównujemy tylko daty (YYYY-MM-DD)

    if filtered_df.empty:
        st.write("No data available for the selected date range.")
        return

    st.subheader("Filtered Data")
    st.dataframe(filtered_df)

    # 🔍 Używamy danych przed filtrowaniem jako głównych danych do raportów
    report_df = df  # Zamiast `filtered_df`, używamy pełnego DataFrame `df`

    # 📊 Przykładowy raport - Suma uszczelek na firmę
    seals_per_company = report_df.groupby('Company')['Seal Count'].sum().sort_values(ascending=False)
    st.subheader("Total Seals Produced by Company")
    st.bar_chart(seals_per_company)

    # 📊 Przykładowy raport - Suma uszczelek na operatora
    seals_per_operator = report_df.groupby('Operator')['Seal Count'].sum().sort_values(ascending=False)
    st.subheader("Total Seals Produced by Operator")
    st.bar_chart(seals_per_operator)

    # 📊 Przykładowy raport - Suma uszczelek na typ uszczelki
    seals_per_type = report_df.groupby('Seal Type')['Seal Count'].sum().sort_values(ascending=False)
    st.subheader("Total Seals Produced by Seal Type")
    st.bar_chart(seals_per_type)
