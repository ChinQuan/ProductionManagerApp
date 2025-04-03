import streamlit as st
import pandas as pd
import datetime

def add_work_minutes(start_datetime, work_minutes, max_days=365):
    total_minutes = 0
    days_processed = 0

    while work_minutes > 0:
        if days_processed > max_days:
            st.error("⚠️ Przekroczono maksymalny limit dni (365). Sprawdź dane wejściowe.")
            return None

        if start_datetime.weekday() < 4:  # Poniedziałek - Czwartek
            work_day_minutes = 510  # 8.5h = 510 minut (9.5h - 1h przerwy)
        elif start_datetime.weekday() == 4:  # Piątek (Praktykant)
            work_day_minutes = 450  # 7.5h = 450 minut (8.5h - 1h przerwy)
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

def format_time(minutes):
    if minutes < 1:
        return f"{int(minutes * 60)}s"
    elif minutes < 60:
        return f"{int(minutes)}m"
    else:
        hours = int(minutes // 60)
        remaining_minutes = int(minutes % 60)
        return f"{hours}h {remaining_minutes}m" if remaining_minutes > 0 else f"{hours}h"

def show_calculator(df):
    st.header("📅 Production Calculator")

    # Zmienna sesyjna na przechowywanie zleceń do kalkulacji
    if 'orders' not in st.session_state:
        st.session_state.orders = []

    if not df.empty and 'Seal Type' in df.columns:
        seal_types = list(df['Seal Type'].unique())
    else:
        seal_types = ['Standard Soft', 'Standard Hard', 'Custom Soft', 'Custom Hard', 'V-Rings', 'Special']
    
    selected_seal_type = st.selectbox("Select Seal Type", seal_types)
    order_quantity = st.number_input("Order Quantity", min_value=1, step=1)
    average_time_per_seal = st.number_input("Enter Average Time per Seal (minutes)", min_value=0.0, step=0.1)

    if st.button("Add Order to Calculation"):
        st.session_state.orders.append({
            "Seal Type": selected_seal_type,
            "Order Quantity": order_quantity,
            "Average Time per Seal": average_time_per_seal
        })
        st.success(f"✅ Order '{selected_seal_type}' added successfully!")

    if st.session_state.orders:
        st.subheader("📝 Orders to Calculate")
        
        # Tabela z dodanymi zleceniami
        orders_df = pd.DataFrame(st.session_state.orders)
