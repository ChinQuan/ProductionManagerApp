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

# Konfiguracja aplikacji
st.set_page_config(page_title="Production Manager App", layout="wide")
st.title("Production Manager App")  # ✅ Nazwa aplikacji widoczna w panelu logowania

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
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
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

    # Zakładki dostępne tylko po zalogowaniu
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Home", "Production Charts", "Calculator", "User Management", "Reports", "Average Production Time"
    ])

    # Zakładka Home
    with tab1:
        st.header("📊 Production Data Overview")
        
        if st.session_state.user is not None:
            # ✅ Formularz dodawania zleceń po prawej stronie
            st.sidebar.subheader("➕ Add New Completed Order")
            
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
    # ✅ Wyświetlanie tabeli z obecnymi zleceniami tylko, jeśli użytkownik jest zalogowany i dane istnieją
    if st.session_state.user is not None and not df.empty:
        st.subheader("📋 Current Production Orders")
        st.dataframe(df)

    # Zakładka Production Charts
    with tab2:
        if st.session_state.user is not None:
            show_charts(df)
        else:
            st.warning("🔒 Please log in to view Production Charts.")

    # Zakładka Calculator
    with tab3:
        if st.session_state.user is not None:
            show_calculator(df)
        else:
            st.warning("🔒 Please log in to access the Calculator.")

    # Zakładka User Management (tylko dla Admina)
    with tab4:
        if st.session_state.user is not None and st.session_state.user['Role'] == 'Admin':
            show_user_management(users_df, save_data_to_gsheets)
        else:
            st.warning("🔒 Access restricted to Admins only.")

    # Zakładka Reports
    with tab5:
        if st.session_state.user is not None:
            show_reports(df)
        else:
            st.warning("🔒 Please log in to access Reports.")

    # Zakładka Average Production Time
    with tab6:
        if st.session_state.user is not None:
            calculate_average_time(df)
        else:
            st.warning("🔒 Please log in to view Average Production Time.")
