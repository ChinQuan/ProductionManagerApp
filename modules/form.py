import streamlit as st
import pandas as pd
import datetime

def show_form(df, save_data_to_gsheets):
    st.sidebar.header("➕ Add New Completed Order")
    
    # 🔥 Sprawdzenie, czy użytkownik jest zalogowany
    if 'user' not in st.session_state or st.session_state.user is None:
        st.sidebar.warning("Please log in to add a new order.")
        return df  # 🔑 Jeżeli użytkownik nie jest zalogowany, zwracamy oryginalny DataFrame

    # 🔑 Pobranie nazwy użytkownika
    operator_name = st.session_state.user['Username'] if st.session_state.user is not None else ""

    # 🔥 WAŻNE: Przycisk submit musi być wewnątrz `st.form()`
    with st.sidebar.form(key="production_form", clear_on_submit=True):
        
        # 📅 1. Wybór daty
        date = st.date_input("Production Date", value=datetime.date.today())
        
        # 🏢 2. Wybór firmy
        company = st.text_input("Company Name", placeholder="Enter company name")
        
        # 👷 3. Wybór operatora (przypisany użytkownik)
        operator = st.text_input("Operator", value=operator_name, disabled=True)  # Teraz pole jest wyświetlane, ale nie można go zmienić
        
        # 🪙 4. Wybór typu uszczelki
        seal_type = st.selectbox("Seal Type", ['Standard Soft', 'Standard Hard', 'Custom Soft', 'Custom Hard', 'V-Rings', 'Stack'])

        # 📋 Dodatkowe pola dla wybranych typów uszczelek
        profile = "N/A"
        actual_seal_count = 0
        seals_count = 0
        
        if seal_type in ['Standard Hard', 'Standard Soft']:
            profile = st.text_input("Enter Seal Profile (e.g., Profile A, Profile B)", placeholder="Profile A")

        if seal_type == 'Stack':
            actual_seal_count = st.number_input("Enter Actual Number of Seals in Stack", min_value=1, step=1)
        
        if seal_type != 'Stack':
            seals_count = st.number_input("Number of Seals", min_value=0, step=1)
        
        # 📋 Pola wspólne dla każdego typu uszczelki
        production_time = st.number_input("Production Time (Minutes)", min_value=0.0, step=0.1)
        downtime = st.number_input("Downtime (Minutes)", min_value=0.0, step=0.1)
        downtime_reason = st.text_input("Reason for Downtime", placeholder="Enter reason for downtime (if any)")
        
        # ✅ Przycisk zapisu (MUSI być wewnątrz formularza)
        submitted = st.form_submit_button("Save Entry")
        
        if submitted:
            if seal_type == 'Stack' and actual_seal_count > 0:
                total_seals = actual_seal_count
            else:
                total_seals = seals_count
            
            # 🔑 Walidacja danych przed zapisem
            if not company:
                st.sidebar.error("⚠️ Company name is required.")
            elif total_seals <= 0:
                st.sidebar.error("⚠️ The number of seals must be greater than zero.")
            else:
                # 📦 Dodawanie nowego wiersza do DataFrame
                new_entry = {
                    'Date': date,
                    'Company': company,
                    'Operator': operator_name,
                    'Seal Type': seal_type,
                    'Profile': profile if profile else "N/A",
                    'Seal Count': total_seals,
                    'Production Time': production_time,
                    'Downtime': downtime,
                    'Reason for Downtime': downtime_reason if downtime_reason else "N/A"
                }
                
                df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
                save_data_to_gsheets(df)
                st.sidebar.success("✅ Order saved successfully!")

    return df
