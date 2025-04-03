import streamlit as st
import pandas as pd
import datetime

def show_form(df, save_data_to_gsheets):
    st.sidebar.header("➕ Add New Completed Order")
    
    with st.sidebar.form("production_form", clear_on_submit=True):
        date = st.date_input("Production Date", value=datetime.date.today())
        company = st.text_input("Company Name")
        operator = st.text_input("Operator", value=st.session_state.user['Username'])
        
        seal_type = st.selectbox("Seal Type", ['Standard Soft', 'Standard Hard', 'Custom Soft', 'Custom Hard', 'V-Rings', 'Stack'])
        
        profile = None
        if seal_type in ['Standard Hard', 'Standard Soft']:
            profile = st.text_input("Enter Seal Profile (e.g., Profile A, Profile B)")
        
        actual_seal_count = None
        if seal_type == 'Stack':
            actual_seal_count = st.number_input("Enter Actual Number of Seals in Stack", min_value=1, step=1)
        
        seals_count = st.number_input("Number of Seals (or Stacks)", min_value=0, step=1)
        
        production_time = st.number_input("Production Time (Minutes)", min_value=0.0, step=0.1)
        downtime = st.number_input("Downtime (Minutes)", min_value=0.0, step=0.1)
        downtime_reason = st.text_input("Reason for Downtime")
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
