import streamlit as st
import pandas as pd

def calculate_average_time(df):
    st.header("⏳ Average Production Time Analysis")

    if df.empty:
        st.write("No data available to calculate average production time.")
        return

    # Dodajemy nowy typ uszczelek "Special" (jeśli nie ma w danych)
    if 'Seal Type' not in df.columns or 'Company' not in df.columns:
        st.write("Required columns not found in data.")
        return

    seal_types = ['Standard Soft', 'Standard Hard', 'Custom Soft', 'Custom Hard', 'V-Rings', 'Special']
    average_times = {}

    # ✅ Analiza na podstawie typu uszczelki
    for seal_type in seal_types:
        filtered_df = df[df['Seal Type'] == seal_type]

        if not filtered_df.empty:
            total_production_time = filtered_df['Production Time'].sum()
            total_seals_count = filtered_df['Seal Count'].sum()

            if total_seals_count > 0:
                average_time_per_seal = total_production_time / total_seals_count
                seals_per_minute = 1 / average_time_per_seal if average_time_per_seal > 0 else 0
                average_times[seal_type] = (average_time_per_seal, seals_per_minute)
            else:
                average_times[seal_type] = (None, None)
        else:
            average_times[seal_type] = (None, None)

    # ✅ Wyświetlanie wyników dla typu uszczelek
    st.subheader("📊 By Seal Type")
    result_df = pd.DataFrame(
        [(seal_type, at[0], at[1]) for seal_type, at in average_times.items()],
        columns=['Seal Type', 'Average Time per Seal (min)', 'Seals Produced per Minute (UPM)']
    )
    st.table(result_df)

    # ✅ Analiza na podstawie firmy
    companies = df['Company'].unique()
    company_times = {}

    for company in companies:
        filtered_df = df[df['Company'] == company]

        if not filtered_df.empty:
            total_production_time = filtered_df['Production Time'].sum()
            total_seals_count = filtered_df['Seal Count'].sum()

            if total_seals_count > 0:
                average_time_per_seal = total_production_time / total_seals_count
                seals_per_minute = 1 / average_time_per_seal if average_time_per_seal > 0 else 0
                company_times[company] = (average_time_per_seal, seals_per_minute)
            else:
                company_times[company] = (None, None)
        else:
            company_times[company] = (None, None)

    # ✅ Wyświetlanie wyników dla firm
    st.subheader("📊 By Company")
    company_df = pd.DataFrame(
        [(company, ct[0], ct[1]) for company, ct in company_times.items()],
        columns=['Company', 'Average Time per Seal (min)', 'Seals Produced per Minute (UPM)']
    )
    st.table(company_df)
