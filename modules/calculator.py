import streamlit as st
import pandas as pd
import datetime

def add_work_minutes(start_datetime, work_minutes, selected_seal_type, max_days=365):
    """Dodaje określoną liczbę minut pracy do daty i czasu, uwzględniając godziny pracy."""
    total_minutes = 0
    days_processed = 0

    while work_minutes > 0:
        if days_processed > max_days:
            st.error("⚠️ Przekroczono maksymalny limit dni (365). Sprawdź dane wejściowe.")
            return None

        if start_datetime.weekday() < 4:  # Poniedziałek - Czwartek
            start_time = datetime.time(6, 30)
            end_time = datetime.time(17, 0)
            work_day_minutes = (datetime.datetime.combine(start_datetime.date(), end_time) - 
                                datetime.datetime.combine(start_datetime.date(), start_time)).total_seconds() / 60 - 60  # Odejmujemy 1h na lunch
            
        elif start_datetime.weekday() == 4:  # Piątek (Praktykant)
            start_time = datetime.time(8, 30)
            end_time = datetime.time(17, 0)
            work_day_minutes = (datetime.datetime.combine(start_datetime.date(), end_time) - 
                                datetime.datetime.combine(start_datetime.date(), start_time)).total_seconds() / 60 - 60  # Odejmujemy 1h na lunch
        else:
            start_datetime += datetime.timedelta(days=1)
            days_processed += 1
            continue

        if work_minutes <= work_day_minutes:
            total_minutes += work_minutes
            return start_datetime + datetime.timedelta(minutes=total_minutes)
        else:
            work_minutes -= work_day_minutes
            total_minutes += work_day_minutes
            start_datetime += datetime.timedelta(days=1)
            days_processed += 1

    return start_datetime

def show_calculator(df):
    st.header("📅 Production Calculator")

    if df.empty:
        st.warning("🚫 No production data available. You can enter data manually below.")
        
    # Typy uszczelek z formularza dodawania zleceń (jeśli df jest pusty, to ręczne wpisywanie)
    if not df.empty and 'Seal Type' in df.columns:
        seal_types = list(df['Seal Type'].unique())
    else:
        seal_types = ['Standard Soft', 'Standard Hard', 'Custom Soft', 'Custom Hard', 'V-Rings', 'Special']
    
    selected_seal_type = st.selectbox("Select Seal Type", seal_types)
    order_quantity = st.number_input("Order Quantity", min_value=1, step=1)
    start_date = st.date_input("Start Date", value=datetime.date.today())
    start_time = st.time_input("Start Time", value=datetime.time(6, 30))

    # Przekształcenie start_date i start_time w datetime
    start_datetime = datetime.datetime.combine(start_date, start_time)

    if not df.empty and 'Seal Type' in df.columns and 'Production Time' in df.columns and 'Seal Count' in df.columns:
        filtered_df = df[df['Seal Type'] == selected_seal_type]

        if not filtered_df.empty:
            total_production_time = filtered_df['Production Time'].sum()
            total_seals = filtered_df['Seal Count'].sum()

            if total_seals > 0:
                average_time_per_seal = total_production_time / total_seals
            else:
                average_time_per_seal = None
        else:
            average_time_per_seal = None
    else:
        average_time_per_seal = None

    # 🔥 Jeśli średni czas jest dostępny, używamy go, w przeciwnym razie pytamy użytkownika o ręczne dane
    if average_time_per_seal is not None:
        st.success(f"📈 Average Time per Seal (from Data): {average_time_per_seal:.2f} minutes")
        estimated_time = average_time_per_seal * order_quantity
    else:
        average_time_per_seal = st.number_input(
            "Enter Average Time per Seal (minutes)", 
            min_value=0.0, step=0.1
        )
        estimated_time = average_time_per_seal * order_quantity

    if st.button("Calculate Estimated Completion Time"):
        estimated_end_datetime = add_work_minutes(start_datetime, estimated_time, selected_seal_type)
        
        if estimated_end_datetime:
            st.success(f"✅ Estimated Completion Time: {estimated_end_datetime.strftime('%Y-%m-%d %H:%M')}")
        else:
            st.error("⚠️ Nie udało się oszacować czasu produkcji. Sprawdź dane wejściowe.")
