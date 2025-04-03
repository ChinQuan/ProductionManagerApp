import streamlit as st
import pandas as pd
import datetime

# Normalne godziny pracy (poniedziałek - czwartek)
WORK_START = datetime.time(6, 30)
WORK_END = datetime.time(17, 0)
LUNCH_START = datetime.time(12, 0)
LUNCH_END = datetime.time(13, 0)

# Godziny pracy praktykanta
PRAKTIKANT_START = datetime.time(8, 30)
PRAKTIKANT_END = datetime.time(17, 0)
PRAKTIKANT_ALLOWED_TYPES = ["Standard Hard", "Standard Soft"]

# Dni pracy praktykanta: Poniedziałek, Wtorek, Środa, Piątek
PRAKTIKANT_DAYS = [0, 1, 2, 4]  # 0 = Poniedziałek, 1 = Wtorek, 2 = Środa, 4 = Piątek

def is_workday(date):
    return date.weekday() in [0, 1, 2, 3]  # Poniedziałek - Czwartek

def is_praktikant_day(date):
    return date.weekday() in PRAKTIKANT_DAYS

def add_work_minutes(start_datetime, minutes, order_type):
    while minutes > 0:
        current_time = start_datetime.time()
        current_day = start_datetime.date()
        is_praktikant = is_praktikant_day(current_day)
        
        if is_workday(current_day):
            work_start = WORK_START
            work_end = WORK_END
        elif is_praktikant:
            work_start = PRAKTIKANT_START
            work_end = PRAKTIKANT_END
            
            if order_type not in PRAKTIKANT_ALLOWED_TYPES:
                start_datetime += datetime.timedelta(days=1)
                continue
        else:
            start_datetime += datetime.timedelta(days=1)
            continue

        if current_time < work_start:
            start_datetime = datetime.datetime.combine(current_day, work_start)
            continue

        if current_time >= work_end:
            start_datetime += datetime.timedelta(days=1)
            continue

        if LUNCH_START <= current_time < LUNCH_END:
            start_datetime = datetime.datetime.combine(current_day, LUNCH_END)
            continue

        end_of_day = datetime.datetime.combine(current_day, work_end)
        minutes_until_end_of_day = (end_of_day - start_datetime).total_seconds() / 60

        if minutes <= minutes_until_end_of_day:
            start_datetime += datetime.timedelta(minutes=minutes)
            minutes = 0
        else:
            minutes -= minutes_until_end_of_day
            start_datetime = end_of_day

    return start_datetime

def show_calculator(df):
    st.header("📅 Production Planner & Calculator")
    
    # 📥 Wczytanie danych o średnich czasach produkcji
    average_times = {}
    for seal_type in df['Seal Type'].unique():
        filtered_df = df[df['Seal Type'] == seal_type]
        if not filtered_df.empty:
            total_time = filtered_df['Production Time'].sum()
            total_seals = filtered_df['Seal Count'].sum()
            
            if total_seals > 0:
                avg_time_per_seal = total_time / total_seals
                average_times[seal_type] = avg_time_per_seal
            else:
                average_times[seal_type] = None

    # 📥 Kalkulator na podstawie pliku Excel
    st.subheader("📋 Excel File Planner")
    uploaded_file = st.file_uploader("Upload Planned Orders Excel File", type=["xlsx"])
    
    if uploaded_file is not None:
        planned_orders = pd.read_excel(uploaded_file)
        
        required_columns = ["Date", "Company", "Seal Type", "Quantity"]
        if not all(column in planned_orders.columns for column in required_columns):
            st.error(f"❌ File must contain columns: {', '.join(required_columns)}")
            return
        
        planned_orders["Date"] = pd.to_datetime(planned_orders["Date"], errors='coerce')
        st.dataframe(planned_orders)
        
        total_estimated_time = 0
        for index, row in planned_orders.iterrows():
            seal_type = row['Seal Type']
            quantity = row['Quantity']
            
            if seal_type in average_times and average_times[seal_type] is not None:
                estimated_time = average_times[seal_type] * quantity
                total_estimated_time += estimated_time
        
        start_date = planned_orders["Date"].min()
        start_datetime = datetime.datetime.combine(start_date.date(), WORK_START)
        estimated_end_datetime = add_work_minutes(start_datetime, total_estimated_time, seal_type)

        st.write(f"📅 Estimated End Date & Time: {estimated_end_datetime.strftime('%Y-%m-%d %H:%M')}")

    # 📊 Szybki kalkulator
    st.subheader("📌 Quick Production Calculator")
    
    available_seal_types = list(average_times.keys())
    selected_seal_type = st.selectbox("Select Seal Type", available_seal_types)
    available_companies = df['Company'].unique()
    selected_company = st.selectbox("Select Company", available_companies)
    quantity = st.number_input("Quantity", min_value=1, step=1)

    if st.button("Calculate Production Time"):
        if selected_seal_type in average_times and average_times[selected_seal_type] is not None:
            estimated_time = average_times[selected_seal_type] * quantity
            start_date = datetime.datetime.now()
            estimated_end_datetime = add_work_minutes(start_date, estimated_time, selected_seal_type)
            st.write(f"📅 Estimated End Date & Time: {estimated_end_datetime.strftime('%Y-%m-%d %H:%M')}")
        else:
            st.write("⚠️ No data available for this seal type.")
