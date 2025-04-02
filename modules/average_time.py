import streamlit as st
import pandas as pd

def calculate_average_time(df):
    st.header("⏳ Average Production Time per Seal Type")

    if df.empty:
        st.write("No data available to calculate average production time.")
        return

    # Dodajemy nowy typ uszczelek "Special" (jeśli nie ma w danych)
    if 'Seal Type' not in df.columns:
        st.write("Seal Type column not found.")
        return

    seal_types = ['Standard Soft', 'Standard Hard', 'Custom Soft', 'Custom Hard', 'V-Rings', 'Special']

    average_times = {}

    for seal_type in seal_types:
        filtered_df = df[df['Seal Type'] == seal_type]

        if not filtered_df.empty:
            # Obliczamy całkowity czas produkcji i ilość wyprodukowanych uszczelek
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

    # Wyświetlamy wyniki w tabeli
    result_df = pd.DataFrame(
        [(seal_type, at[0], at[1]) for seal_type, at in average_times.items()],
        columns=['Seal Type', 'Average Time per Seal (min)', 'Seals Produced per Minute (UPM)']
    )
    st.table(result_df)
