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
from modules.admin import show_admin_panel

# Inicjalizacja aplikacji
st.set_page_config(page_title="Production Manager App", layout="wide")
st.title("Production Manager App")

# Funkcja łączenia z Google Sheets
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

# Funkcja ładowania danych użytkowników
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

# Funkcja ładowania danych produkcyjnych
def load_data_from_gsheets():
    client = connect_to_gsheets()
    try:
        sheet = client.open("ProductionManagerApp").sheet1
        data = sheet.get_all_records()
        if data:
            return pd.DataFrame(data)
    except Exception as e:
        st.error(f"❌ Error loading production data: {e}")
    return pd.DataFrame(columns=['Date', 'Company', 'Seal Count', 'Operator', 'Seal Type', 'Production Time', 'Downtime', 'Reason for Downtime'])
# Funkcja zapisywania danych produkcyjnych
def save_data_to_gsheets(df):
    client = connect_to_gsheets()
    sheet = client.open("ProductionManagerApp").sheet1
    df = df.astype(str)
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())

# Wczytywanie danych
users_df = load_users()
df = load_data_from_gsheets()

# Inicjalizacja sesji
if 'user' not in st.session_state:
    st.session_state.user = None

# Panel logowania - widoczny TYLKO gdy użytkownik nie jest zalogowany
if st.session_state.user is None:
    st.sidebar.title("🔑 Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        user = users_df[(users_df['Username'] == username) & (users_df['Password'] == password)]
        if not user.empty:
            st.session_state.user = user.iloc[0].to_dict()
            st.sidebar.success(f"Logged in as {username}")
        else:
            st.sidebar.error("Invalid username or password")
# ✅ Wyświetlanie zakładek TYLKO po zalogowaniu
if st.session_state.user is not None:
    st.sidebar.write(f"✅ Logged in as {st.session_state.user['Username']}")
    
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.sidebar.success("🔓 You have been logged out successfully.")
        
    # Zakładki widoczne po zalogowaniu
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Home", "Production Charts", "Admin", "Calculator", "Average Time"
    ])

    with tab1:
        st.header("📊 Production Data Overview")
        
        if st.session_state.user['Role'] == 'Admin':
            show_admin_panel(users_df, save_data_to_gsheets, df, "Home")
        
        if not df.empty:
            st.dataframe(df)

            # ✅ Obliczanie średniej produkcji dziennej
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            total_seals = df['Seal Count'].sum()
            total_days = (df['Date'].max() - df['Date'].min()).days + 1
            
            if total_days > 0:
                average_daily_production = total_seals / total_days
                st.metric(label="📈 Average Daily Production", value=f"{average_daily_production:.2f} seals per day")
            else:
                st.write("📅 Not enough data to calculate daily production average.")

    with tab2:
        show_charts(df)

    with tab3:
        if st.session_state.user['Role'] == 'Admin':
            show_user_management(users_df, save_data_to_gsheets)
        else:
            st.warning("🚫 Only Admins can access this section.")

    with tab4:
        show_calculator(df)
    
    with tab5:
        calculate_average_time(df)
