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
from modules.form import show_form  # ✅ Import formularza z modułu

# Konfiguracja aplikacji
st.set_page_config(page_title="Production Manager App", layout="wide")
st.title("Production Manager App")

# Inicjalizacja stanu sesji
if 'user' not in st.session_state:
    st.session_state.user = None

# Funkcja połączenia z Supabase
def connect_to_supabase():
    try:
        url = st.secrets["supabase_url"]
        key = st.secrets["supabase_key"]
        client = create_client(url, key)
        return client
    except Exception as e:
        st.error(f"❌ Error connecting to Supabase: {e}")
        return None

supabase = connect_to_supabase()
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

# Wczytanie użytkowników i danych produkcyjnych
users_df = load_users()
df = load_data_from_supabase()

# Funkcja zapisywania nowego zlecenia do Supabase
def save_order_to_supabase(order_data):
    try:
        response = supabase.table("production_orders").insert(order_data).execute()
        if response.error is None:
            st.sidebar.success("✅ Order successfully saved to Supabase!")
        else:
            st.sidebar.error(f"❌ Failed to save order: {response.error}")
    except Exception as e:
        st.sidebar.error(f"❌ Error saving order: {e}")

# Funkcja aktualizacji istniejącego zlecenia w Supabase
def update_order_in_supabase(order_id, updated_data):
    try:
        response = supabase.table("production_orders").update(updated_data).eq('id', order_id).execute()
        if response.error is None:
            st.sidebar.success("✅ Order successfully updated in Supabase!")
        else:
            st.sidebar.error(f"❌ Failed to update order: {response.error}")
    except Exception as e:
        st.sidebar.error(f"❌ Error updating order: {e}")

# Funkcja usuwania zlecenia z Supabase
def delete_order_from_supabase(order_id):
    try:
        response = supabase.table("production_orders").delete().eq('id', order_id).execute()
        if response.error is None:
            st.sidebar.success("✅ Order successfully deleted from Supabase!")
        else:
            st.sidebar.error(f"❌ Failed to delete order: {response.error}")
    except Exception as e:
        st.sidebar.error(f"❌ Error deleting order: {e}")
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
        
        if st.session_state.user is not None and not df.empty:
            st.subheader("📋 Current Production Orders")
            st.dataframe(df)
            
            if not df.empty and 'Date' in df.columns:
                valid_dates = df['Date'].dropna()
                if len(valid_dates) > 0:
                    total_seals = df['Seal Count'].sum()
                    total_days = (valid_dates.max() - valid_dates.min()).days + 1

                    if total_days > 0:
                        average_daily_production = total_seals / total_days
                        st.write(f"### 📈 Average Daily Production: {average_daily_production:.2f} seals per day")
                    else:
                        st.write("### 📈 Average Daily Production: Not enough data to calculate.")
                else:
                    st.write("### 📈 Average Daily Production: No valid dates available.")

        df = show_form(df, supabase)
    
    with tab2:
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
