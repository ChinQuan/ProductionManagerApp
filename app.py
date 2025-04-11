import streamlit as st
import pandas as pd
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Importowanie modułów
from modules.reports import show_reports
from modules.charts import show_charts
from modules.backup import show_backup_option
from modules.user_management import show_user_management
from modules.average_time import calculate_average_time
from modules.calculator import show_calculator
from modules.form import show_form  # ✅ Import formularza z modułu

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
        st.error(f"❌ Error loading users: {e}")
    return pd.DataFrame(columns=['Username', 'Password', 'Role'])

# Funkcja ładowania danych produkcyjnych z Google Sheets
def load_data_from_gsheets():
    client = connect_to_gsheets()
    try:
        sheet = client.open("ProductionManagerApp").sheet1
        data = sheet.get_all_records()
        if data:
            df = pd.DataFrame(data)
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.date  # ✅ Tylko data, bez godzin
            df = df.dropna(subset=['Date'])
            return df
    except Exception as e:
        st.error(f"❌ Error loading production data: {e}")
    return pd.DataFrame(columns=['Date', 'Company', 'Operator', 'Seal Type', 'Seal Count', 'Profile', 'Production Time', 'Downtime', 'Reason for Downtime'])

# Funkcja zapisywania danych do Google Sheets
def save_data_to_gsheets(dataframe):
    client = connect_to_gsheets()
    sheet = client.open("ProductionManagerApp").sheet1
    dataframe = dataframe.astype(str)
    sheet.clear()
    sheet.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())

# Wczytanie użytkowników i danych produkcyjnych
users_df = load_users()
df = load_data_from_gsheets()
# Funkcja logowania
def login(username, password, users_df):
    user = users_df[(users_df['Username'] == username) & (users_df['Password'] == password)]
    if not user.empty:
        return user.iloc[0]
    return None

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

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Home", "Production Charts", "Calculator", "User Management", "Reports", "Average Production Time"
    ])

    # Zakładka Home
    with tab1:
        st.header("📊 Production Data Overview")
        
        if st.session_state.user is not None and not df.empty:
            st.subheader("📋 Current Production Orders")
            st.dataframe(df)
            
            if 'Date' in df.columns:
                total_seals = df['Seal Count'].sum()
                working_days_df = df[pd.to_datetime(df['Date']).dt.dayofweek < 5]
                unique_working_days = working_days_df['Date'].nunique()
                unique_order_days = df['Date'].nunique()

                if unique_working_days > 0:
                if unique_working_days > 0:
                    average_working_days = total_seals / unique_working_days
                    st.write(f"### 📈 Avg. Daily Production (Working Days Only): {average_working_days:.2f} seals per day")
                else:
                    st.warning("Brak dostępnych dni roboczych do obliczenia średniej produkcji w dni robocze.")
                    st.write(f"### 📈 Avg. Daily Production (Working Days Only): {average_working_days:.2f} seals per day")
                
                if unique_order_days > 0:
                if unique_order_days > 0:
                    average_order_days = total_seals / unique_order_days
                    st.write(f"### 📊 Avg. Daily Production (All Days): {average_order_days:.2f} seals per day")
                else:
                    st.warning("Brak dostępnych dni do obliczenia średniej produkcji.")
                    st.write(f"### 📈 Avg. Daily Production (Order Dates Only): {average_order_days:.2f} seals per day")

        df = show_form(df, save_data_to_gsheets)

    with tab2:
        if st.session_state.user is not None:
            show_charts(df)
        else:
            st.warning("🔒 Please log in to view Production Charts.")

    with tab5:
        if st.session_state.user is not None:
            show_reports(df)
        else:
            st.warning("🔒 Please log in to access Reports.")

    with tab3:
        if st.session_state.user is not None:
            show_calculator(df)
        else:
            st.warning("🔒 Please log in to access the Calculator.")

    with tab4:
        if st.session_state.user is not None and st.session_state.user['Role'] == 'Admin':
            show_user_management(users_df, save_data_to_gsheets)
        else:
            st.warning("🔒 Access restricted to Admins only.")

    with tab6:
        if st.session_state.user is not None:
            calculate_average_time(df)
        else:
            st.warning("🔒 Please log in to view Average Production Time.")



def save_users_to_gsheets(users_df):
    client = connect_to_gsheets()
    try:
        sheet = client.open("ProductionManagerApp").worksheet("Users")
    except gspread.exceptions.WorksheetNotFound:
        sheet = client.open("ProductionManagerApp").add_worksheet(title="Users", rows="100", cols="20")
    sheet.clear()
    sheet.update([users_df.columns.values.tolist()] + users_df.values.tolist())

    # Backup lokalny
    users_df.to_excel("users_backup.xlsx", index=False)
