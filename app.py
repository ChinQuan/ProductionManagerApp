import streamlit as st
import pandas as pd
import os
import datetime
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

# Importowanie modułów
from modules.reports import show_reports
from modules.charts import show_charts
from modules.backup import show_backup_option
from modules.user_management import show_user_management
from modules.average_time import calculate_average_time
from modules.calculator import show_calculator  # Nowy moduł!

# Konfiguracja aplikacji
st.set_page_config(page_title="Production Manager App", layout="wide")
st.title("Production Manager App")

# Inicjalizacja stanu sesji
if 'user' not in st.session_state:
    st.session_state.user = None

# Funkcja połączenia z Google Sheets
def connect_to_gsheets():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"
    ]

    credentials = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials, scope)
    client = gspread.authorize(creds)
    
    return client

# Funkcja ładowania danych użytkowników z Google Sheets
def load_users():
    client = connect_to_gsheets()
    try:
        sheet = client.open("ProductionManagerApp").worksheet("Users")
        data = sheet.get_all_records()
        if data:
            return pd.DataFrame(data)
    except Exception as e:
        st.error(f"❌ Błąd podczas ładowania użytkowników: {e}")
    return pd.DataFrame(columns=['Username', 'Password', 'Role'])

# Funkcja zapisywania użytkowników do Google Sheets
def save_users_to_gsheets(users_df):
    client = connect_to_gsheets()
    sheet = client.open("ProductionManagerApp").worksheet("Users")
    users_df = users_df.astype(str)
    sheet.clear()
    sheet.update([users_df.columns.values.tolist()] + users_df.values.tolist())
# Funkcja ładowania danych produkcyjnych z arkusza Google Sheets
def load_data_from_gsheets():
    client = connect_to_gsheets()
    try:
        sheet = client.open("ProductionManagerApp").sheet1
        data = sheet.get_all_records()
        if data:
            return pd.DataFrame(data)
    except Exception as e:
        st.error(f"❌ Błąd podczas ładowania danych produkcyjnych: {e}")
    return pd.DataFrame(columns=['Date', 'Company', 'Seal Count', 'Operator', 'Seal Type', 'Production Time', 'Downtime', 'Reason for Downtime'])

# Funkcja zapisywania danych produkcyjnych do Google Sheets
def save_data_to_gsheets(dataframe):
    client = connect_to_gsheets()
    sheet = client.open("ProductionManagerApp").sheet1
    
    dataframe['Date'] = dataframe['Date'].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) else None)
    dataframe = dataframe.astype(str)
    sheet.clear()
    sheet.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())

# Funkcja logowania
def login(username, password, users_df):
    user = users_df[(users_df['Username'] == username) & (users_df['Password'] == password)]
    if not user.empty:
        return user.iloc[0]
    return None

# Wczytanie użytkowników i danych produkcyjnych
users_df = load_users()
df = load_data_from_gsheets()

# ✅ Konwersja kolumny 'Date' do datetime
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# Panel logowania
if st.session_state.user is None:
    st.sidebar.title("🔑 Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        user = login(username, password, users_df)
        if user is not None:
            st.session_state.user = user
            st.sidebar.success(f"Logged in as {user['Username']}")
        else:
            st.sidebar.error("Invalid username or password")
else:
    st.sidebar.write(f"✅ Logged in as {st.session_state.user['Username']}")
    if st.sidebar.button("Logout"):
        st.session_state.user = None
# Zakładki
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "Home", "Production Charts", "User Management", "Reports", "Backup", "Average Production Time", "Production Calculator", "Edit/Delete Orders"
])

with tab1:
    st.header("📊 Production Data Overview")
    st.dataframe(df)

with tab2:
    show_charts(df)

with tab3:
    if st.session_state.user and st.session_state.user['Role'] == 'Admin':
        show_user_management(users_df, save_users_to_gsheets)

with tab4:
    show_reports(df)

with tab5:
    show_backup_option(df, save_data_to_gsheets)

with tab6:
    calculate_average_time(df)

with tab7:
    show_calculator(df)

with tab8:
    if st.session_state.user and st.session_state.user['Role'] == 'Admin':
        st.header("✏️ Edit or Delete Orders")
        
        if not df.empty:
            selected_index = st.selectbox("Select Order to Edit/Delete", df.index)
            
            if selected_index is not None:
                selected_row = df.loc[selected_index]
                
                with st.form("edit_order_form"):
                    date = st.date_input("Edit Production Date", value=selected_row['Date'])
                    company = st.text_input("Edit Company Name", value=selected_row['Company'])
                    operator = st.text_input("Edit Operator", value=selected_row['Operator'])
                    seal_type = st.text_input("Edit Seal Type", value=selected_row['Seal Type'])
                    seals_count = st.number_input("Edit Seal Count", value=int(selected_row['Seal Count']))
                    production_time = st.number_input("Edit Production Time", value=float(selected_row['Production Time']))
                    downtime = st.number_input("Edit Downtime", value=float(selected_row['Downtime']))
                    reason = st.text_input("Edit Reason for Downtime", value=selected_row['Reason for Downtime'])

                    update_button = st.form_submit_button("Update Order")
                    delete_button = st.form_submit_button("Delete Order")
                    
                    if update_button:
                        df.at[selected_index, 'Date'] = date
                        df.at[selected_index, 'Company'] = company
                        df.at[selected_index, 'Operator'] = operator
                        df.at[selected_index, 'Seal Type'] = seal_type
                        df.at[selected_index, 'Seal Count'] = seals_count
                        df.at[selected_index, 'Production Time'] = production_time
                        df.at[selected_index, 'Downtime'] = downtime
                        df.at[selected_index, 'Reason for Downtime'] = reason
                        save_data_to_gsheets(df)
                        st.success("✅ Order updated successfully!")

                    if delete_button:
                        df = df.drop(selected_index)
                        save_data_to_gsheets(df)
                        st.success("✅ Order deleted successfully!")
