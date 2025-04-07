import streamlit as st
import pandas as pd
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from modules.reports import show_reports
from modules.charts import show_charts
from modules.backup import show_backup_option
from modules.user_management import show_user_management
from modules.average_time import calculate_average_time
from modules.calculator import show_calculator
from modules.form import show_form
from streamlit_lottie import st_lottie
import requests

# 📌 Funkcja ładowania animacji Lottie
def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# 🎥 URL animacji wylogowania
logout_animation_url = "https://assets5.lottiefiles.com/packages/lf20_kz5qgtpe.json"
logout_animation = load_lottie_url(logout_animation_url)

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
            st.experimental_rerun()  # 🚀 Odświeżenie po zalogowaniu
        else:
            st.sidebar.error("Invalid username or password")
else:
    st.sidebar.write(f"✅ Logged in as {st.session_state.user['Username']}")
    
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.experimental_rerun()  # 🚀 Odświeżenie po wylogowaniu
        
        # 🎥 Wyświetlenie animacji Lottie po wylogowaniu
        st_lottie(logout_animation, height=300, width=300, key="logout_animation")
        st.warning("You have been logged out successfully.")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Home", "Production Charts", "Calculator", "User Management", "Reports", "Average Production Time"
    ])

    # Zakładka Home
    with tab1:
        st.header("📊 Production Data Overview")
        
        if not df.empty:
            st.subheader("📋 Current Production Orders")
            st.dataframe(df)
            
            if 'Date' in df.columns:
                total_seals = df['Seal Count'].sum()
                working_days_df = df[pd.to_datetime(df['Date']).dt.dayofweek < 5]
                unique_working_days = working_days_df['Date'].nunique()
                unique_order_days = df['Date'].nunique()

                if unique_working_days > 0:
                    average_working_days = total_seals / unique_working_days
                    st.write(f"### 📈 Avg. Daily Production (Working Days Only): {average_working_days:.2f} seals per day")
                
                if unique_order_days > 0:
                    average_order_days = total_seals / unique_order_days
                    st.write(f"### 📈 Avg. Daily Production (Order Dates Only): {average_order_days:.2f} seals per day")

        df = show_form(df, save_data_to_gsheets)

    with tab2:
        show_charts(df)

    with tab3:
        show_calculator(df)

    with tab4:
        if st.session_state.user['Role'] == 'Admin':
            show_user_management(users_df, save_data_to_gsheets)

    with tab5:
        show_reports(df)

    with tab6:
        calculate_average_time(df)
