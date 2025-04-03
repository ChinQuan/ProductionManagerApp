import streamlit as st
import pandas as pd

def show_calculator(df):
    st.header("🧮 Production Time Calculator")

    if df.empty:
        st.warning("❌ No production data available. Add entries to calculate production time.")
        return

    # Filtrujemy unikalne typy uszczelek z danych wprowadzonych do aplikacji
    seal_types = df['Seal Type'].unique().tolist()
    
    if not seal_types:
        st.warning("❌ No seal types available. Add entries to calculate production time.")
        return

    # Wybór typu uszczelki
    seal_type = st.selectbox("Seal Type", seal_types)

    # Wprowadzenie ilości sztuk
    quantity = st.number_input("Quantity", min_value=1, step=1)

    if st.button("Calculate Production Time"):
        # Filtrujemy dane dla wybranego typu uszczelki
        filtered_df = df[df['Seal Type'] == seal_type]

        if not filtered_df.empty:
            # Obliczamy średni czas produkcji na sztukę (w minutach)
            filtered_df['Production Time per Piece'] = filtered_df['Production Time'] / filtered_df['Seal Count']
            average_time_per_piece = filtered_df['Production Time per Piece'].mean()

            if pd.notna(average_time_per_piece) and average_time_per_piece > 0:
                # Obliczamy całkowity czas produkcji
                total_time = quantity * average_time_per_piece

                # Przekształcamy czas na godziny, minuty i sekundy
                hours = int(total_time // 60)
                minutes = int(total_time % 60)
                seconds = int((total_time - int(total_time)) * 60)

                st.success(f"🕒 Estimated Production Time for {quantity} '{seal_type}': {hours} hours, {minutes} minutes, {seconds} seconds")
            else:
                st.warning(f"❌ Insufficient data to calculate average production time for '{seal_type}'.")
        else:
            st.warning(f"❌ No data found for the selected seal type: '{seal_type}'.")
