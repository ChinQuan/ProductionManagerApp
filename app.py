import streamlit as st
import pandas as pd
import datetime
import gspread
from google.oauth2.service_account import Credentials

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
st.title("Production Manager App")  # ✅ Nazwa aplikacji widoczna w panelu logowania

# Inicjalizacja stanu sesji
if 'user' not in st.session_state:
    st.session_state.user = None

# Funkcja połączenia z Google Sheets
def connect_to_gsheets():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope
    )
    client = gspread.authorize(credentials)
    
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

# Funkcja logowania
def login(username, password, users_df):
    user = users_df[(users_df['Username'] == username) & (users_df['Password'] == password)]
    if not user.empty:
        return user.iloc[0]
    return None

# Wczytanie użytkowników
users_df = load_users()

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
# Funkcja ładowania danych produkcyjnych z Google Sheets
def load_data_from_gsheets():
    client = connect_to_gsheets()
    try:
        sheet = client.open("ProductionManagerApp").sheet1
        data = sheet.get_all_records()
        
        if data:
            df = pd.DataFrame(data)
            if 'Date' in df.columns:
                df['Date'] = df['Date'].astype(str)
                df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d', errors='coerce').dt.date
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

# Wczytanie danych produkcyjnych
df = load_data_from_gsheets()

# Zakładki dostępne po zalogowaniu
if st.session_state.user is not None:
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
                valid_dates = df['Date'].dropna()
                
                if len(valid_dates) > 0:
                    total_days = (valid_dates.max() - valid_dates.min()).days + 1
                    if total_days > 0:
                        average_daily_production = total_seals / total_days
                        st.write(f"### 📈 Average Daily Production: {average_daily_production:.2f} seals per day")
        df = show_form(df, save_data_to_gsheets)

    # Zakładka Production Charts
    with tab2:
        show_charts(df)

    # Zakładka Calculator
    with tab3:
        show_calculator(df)

    # Zakładka User Management (tylko dla Admina)
    with tab4:
        if st.session_state.user['Role'] == 'Admin':
            show_user_management(users_df, save_data_to_gsheets)
        else:
            st.warning("🔒 Access restricted to Admins only.")

    # Zakładka Reports
    with tab5:
        show_reports(df)

    # Zakładka Average Production Time
    with tab6:
        calculate_average_time(df)

     
