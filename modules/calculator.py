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

    if 'orders' not in st.session_state:
        st.session_state.orders = []

    if df.empty:
        st.error("🚫 No production data available. Add entries first.")
        return
    
    seal_types = df['Seal Type'].unique().tolist()
    companies = df['Company'].unique().tolist()

    selected_company = st.selectbox("Select Company", companies)
    selected_seal_type = st.selectbox("Select Seal Type", seal_types)
    order_quantity = st.number_input("Order Quantity", min_value=1, step=1)

    filtered_df = df[(df['Seal Type'] == selected_seal_type) & (df['Company'] == selected_company)]

    if not filtered_df.empty:
        total_production_time = filtered_df['Production Time'].sum()
        total_seals = filtered_df['Seal Count'].sum()

        if total_seals > 0:
            average_time_per_seal = total_production_time / total_seals
            st.success(f"📈 Average Time per Seal: {format_time(average_time_per_seal)}")
        else:
            average_time_per_seal = 0
    else:
        average_time_per_seal = 0

    if st.button("Add Order to Calculation"):
        if average_time_per_seal > 0:
            st.session_state.orders.append({
                "Company": selected_company,
                "Seal Type": selected_seal_type,
                "Order Quantity": order_quantity,
                "Average Time per Seal (minutes)": average_time_per_seal
            })
            st.success(f"✅ Order '{selected_seal_type}' for '{selected_company}' added successfully!")
        else:
            st.error("⚠️ Cannot add order without valid average time.")

    if st.session_state.orders:
        st.subheader("📝 Orders to Calculate")
        orders_df = pd.DataFrame(st.session_state.orders)
        st.table(orders_df)

        if st.button("Clear All Orders"):
            st.session_state.orders = []
            st.warning("📋 All orders have been cleared.")

        # 📅 Wybieranie przedziału czasu na wykonanie zleceń
        st.subheader("📅 Set Working Time Range")
        start_date = st.date_input("Start Date", value=datetime.date.today())
        start_time = st.time_input("Start Time", value=datetime.time(6, 30))
        end_date = st.date_input("End Date", value=start_date + datetime.timedelta(days=4))
        end_time = st.time_input("End Time", value=datetime.time(17, 0))

        start_datetime = datetime.datetime.combine(start_date, start_time)
        end_datetime = datetime.datetime.combine(end_date, end_time)
        
        # 🧮 Obliczenia dla wszystkich zleceń
        total_time = sum(order["Order Quantity"] * order["Average Time per Seal (minutes)"] for order in st.session_state.orders)
        estimated_end_datetime = add_work_minutes(start_datetime, total_time)

        if estimated_end_datetime:
            formatted_time = format_time(total_time)
            st.success(f"✅ Total Production Time: {formatted_time}")
            st.success(f"✅ Estimated Completion Time: {estimated_end_datetime.strftime('%Y-%m-%d %H:%M')}")

            # 🔔 Sprawdzanie, czy da się zakończyć pracę przed wybranym czasem
            if estimated_end_datetime <= end_datetime:
                st.success("🎉 All orders can be completed within the specified time range!")
            else:
                st.error("⛔ It is not possible to complete all orders within the specified time range.")
        else:
            st.error("⚠️ Calculation failed. Check your input data.")
