import streamlit as st
import pandas as pd
import datetime

def show_form(df, save_data_to_gsheets):
    st.sidebar.header("➕ Add New Completed Order")
    
    # 🔥 WAŻNE: Przycisk submit musi być wewnątrz `st.form()`
    with st.sidebar.form(key="production_form", clear_on_submit=True):
        
        # 📅 1. Wybór daty
        date = st.date_input("Production Date", value=datetime.date.today())
        
        # 🏢 2. Wybór firmy
        company = st.text_input("Company Name")
        
        # 👷 3. Wybór operatora
        operator = st.text_input("Operator", value=st.session_state.user['Username'])
        
        # 🪙 4. Wybór typu uszczelki
        seal_type = st.selectbox("Seal Type", ['Standard Soft', 'Standard Hard', 'Custom Soft', 'Custom Hard', 'V-Rings', 'Stack'])

        profile = None
        actual_seal_count = None
        seals_count = 0
        
        # 🔍 Dodatkowe pola dla wybranych typów uszczelek
        if seal_type in ['Standard Hard', 'Standard Soft']:
            profile = st.text_input("Enter Seal Profile (e.g., Profile A, Profile B)")
        
        if seal_type == 'Stack':
            actual_seal_count = st.number_input("Enter Actual Number of Seals in Stack", min_value=1, step=1)
        
        if seal_type not in ['Stack']:
            seals_count = st.number_input("Number of Seals", min_value=0, step=1)
        
        # 📋 Pola wspólne dla każdego typu uszczelki
        production_time = st.number_input("Production Time (Minutes)", min_value=0.0, step=0.1)
        downtime = st.number_input("Downtime (Minutes)", min_value=0.0, step=0.1)
        downtime_reason = st.text_input("Reason for Downtime")
        
        # ✅ Przycisk zapisu (MUSI być wewnątrz formularza)
        submitted = st.form_submit_button("Save Entry")
        
        if submitted:
            if seal_type == 'Stack' and actual_seal_count:
                total_seals = actual_seal_count
            else:
                total_seals = seals_count
            
            new_entry = {
                'Date': date,
                'Company': company,
                'Operator': operator,
                'Seal Type': seal_type,
                'Profile': profile if profile else "N/A",
                'Seal Count': total_seals,
                'Production Time': production_time,
                'Downtime': downtime,
                'Reason for Downtime': downtime_reason
            }
            
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            save_data_to_gsheets(df)
            st.sidebar.success("✅ Order saved successfully!")

    return df
