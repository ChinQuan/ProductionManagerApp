import streamlit as st
import pandas as pd
import datetime
from supabase import create_client, Client

# Importowanie modułów
from modules.reports import show_reports
from modules.charts import show_charts
from modules.backup import show_backup_option
from modules.user_management import show_user_management
from modules.average_time import calculate_average_time
from modules.calculator import show_calculator
from modules.form import show_form

# Konfiguracja aplikacji
st.set_page_config(page_title="Production Manager App", layout="wide")
st.title("Production Manager App")

# Inicjalizacja stanu sesji
if 'user' not in st.session_state:
    st.session_state.user = None

# Funkcja połączenia z Supabase
def connect_to_supabase():
    url = st.secrets["supabase_url"]
    key = st.secrets["supabase_key"]
    return create_client(url, key)

supabase = connect_to_supabase()

# Sprawdzenie połączenia z Supabase
if supabase:
    st.write("✅ Połączono z Supabase!")
else:
    st.write("❌ Nie udało się połączyć z Supabase.")
# Funkcja ładowania danych użytkowników z Supabase
def load_users():
    try:
        response = supabase.table("users").select("*").execute()
        if response.data:
            return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"❌ Error loading users: {e}")
    return pd.DataFrame(columns=['id', 'Username', 'Password', 'Role'])

# Funkcja ładowania danych produkcyjnych z Supabase
def load_data_from_supabase():
    try:
        response = supabase.table("production_orders").select("*").execute()
        if response.data:
            df = pd.DataFrame(response.data)
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.date
            df = df.dropna(subset=['Date'])
            return df
    except Exception as e:
        st.error(f"❌ Error loading production data: {e}")
    return pd.DataFrame(columns=['id', 'Date', 'Company', 'Operator', 'Seal Type', 'Seal Count', 'Profile', 'Production Time', 'Downtime', 'Reason for Downtime'])

users_df = load_users()
df = load_data_from_supabase()

def login(username, password, users_df):
    user = users_df[(users_df['Username'] == username) & (users_df['Password'] == password)]
    if not user.empty:
        return user.iloc[0]
    return None
if st.session_state.user is None:
    st.sidebar.title("🔑 Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        user = login(username, password, users_df)
        if user is not None:
            st.session_state.user = user
            st.experimental_rerun()
        else:
            st.sidebar.error("Invalid username or password")
else:
    st.sidebar.write(f"✅ Logged in as {st.session_state.user['Username']}")
    
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.experimental_rerun()

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Home", "Production Charts", "Calculator", "User Management", "Reports", "Average Production Time"
    ])

    with tab1:
        st.header("📊 Production Data Overview")
        if not df.empty:
            st.subheader("📋 Current Production Orders")
            st.dataframe(df)

    with tab2:
        if st.session_state.user['Role'] == 'Admin':
            show_charts(df)
    
    with tab3:
        show_calculator(df)
    
    with tab4:
        if st.session_state.user['Role'] == 'Admin':
            show_user_management(users_df, supabase)
    
    with tab5:
        show_reports(df)
    
    with tab6:
        calculate_average_time(df)
