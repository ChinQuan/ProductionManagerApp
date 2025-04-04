import streamlit as st
import pandas as pd
import psycopg2
from psycopg2 import sql

# Konfiguracja aplikacji
st.set_page_config(page_title="Production Manager App", layout="wide")
st.title("Production Manager App")

# Ustawienia Supabase (z `Streamlit Secrets`)
DB_HOST = st.secrets["supabase_host"]
DB_NAME = st.secrets["supabase_db"]
DB_USER = st.secrets["supabase_user"]
DB_PASSWORD = st.secrets["supabase_password"]
DB_PORT = st.secrets.get("supabase_port", 5432)

# Funkcja połączenia z bazą danych
def connect_to_supabase():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    return conn

# Funkcja ładowania danych użytkowników
def load_users():
    try:
        conn = connect_to_supabase()
        query = "SELECT * FROM users;"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Błąd podczas ładowania użytkowników: {e}")
        return pd.DataFrame(columns=['id', 'Username', 'Password', 'Role'])

# Funkcja ładowania danych produkcyjnych
def load_data_from_supabase():
    try:
        conn = connect_to_supabase()
        query = "SELECT * FROM production_orders;"
        df = pd.read_sql(query, conn)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.date
        conn.close()
        return df
    except Exception as e:
        st.error(f"Błąd podczas ładowania danych produkcyjnych: {e}")
        return pd.DataFrame(columns=['id', 'Date', 'Company', 'Operator', 'Seal Type', 'Seal Count', 'Profile', 'Production Time', 'Downtime', 'Reason for Downtime'])

# Wczytanie danych z Supabase
users_df = load_users()
df = load_data_from_supabase()
# Funkcja logowania
def login(username, password, users_df):
    user = users_df[(users_df['Username'] == username) & (users_df['Password'] == password)]
    if not user.empty:
        return user.iloc[0]
    return None

# Panel logowania
if 'user' not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.sidebar.title("🔑 Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        user = login(username, password, users_df)
        if user is not None:
            st.session_state.user = user
            st.sidebar.success(f"Zalogowano jako {user['Username']}")
        else:
            st.sidebar.error("Niepoprawny login lub hasło.")
else:
    st.sidebar.write(f"✅ Zalogowano jako {st.session_state.user['Username']}")

    if st.sidebar.button("Logout"):
        st.session_state.user = None

# Wyświetlanie tabeli użytkowników dla administratora
if st.session_state.user is not None and st.session_state.user['Role'] == 'Admin':
    st.write("📋 Lista użytkowników:")
    st.dataframe(users_df)
# Wyświetlanie danych produkcyjnych
if st.session_state.user is not None and not df.empty:
    st.header("📊 Production Data Overview")
    st.dataframe(df)

# Funkcja zapisywania nowego zlecenia do Supabase
def save_order_to_supabase(order_data):
    try:
        conn = connect_to_supabase()
        cursor = conn.cursor()
        insert_query = sql.SQL("""
            INSERT INTO production_orders (Date, Company, Operator, Seal_Type, Seal_Count, Profile, Production_Time, Downtime, Reason_for_Downtime)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """)
        cursor.execute(insert_query, order_data)
        conn.commit()
        cursor.close()
        conn.close()
        st.success("✅ Zlecenie zapisane pomyślnie!")
    except Exception as e:
        st.error(f"Błąd podczas zapisywania zlecenia: {e}")

# Formularz dodawania zlecenia
if st.session_state.user is not None:
    st.header("📥 Dodaj nowe zlecenie")

    with st.form("new_order_form"):
        Date = st.date_input("Data")
        Company = st.text_input("Firma")
        Operator = st.text_input("Operator")
        Seal_Type = st.text_input("Rodzaj uszczelki")
        Seal_Count = st.number_input("Ilość uszczelek", min_value=0)
        Profile = st.text_input("Profil")
        Production_Time = st.text_input("Czas produkcji")
        Downtime = st.text_input("Przestój")
        Reason_for_Downtime = st.text_input("Powód przestoju")

        submit = st.form_submit_button("Zapisz zlecenie")

        if submit:
            order_data = (Date, Company, Operator, Seal_Type, Seal_Count, Profile, Production_Time, Downtime, Reason_for_Downtime)
            save_order_to_supabase(order_data)
