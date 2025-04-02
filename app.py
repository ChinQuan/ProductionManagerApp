import streamlit as st
import pandas as pd
import os
import datetime
import plotly.express as px

# Konfiguracja aplikacji
st.set_page_config(page_title="Production Manager App", layout="wide")
st.title("Production Manager App")

# Ścieżki plików
current_dir = os.getcwd()
DATA_FILE = os.path.join(current_dir, 'Production_orders.csv')
USERS_FILE = os.path.join(current_dir, 'users.xlsx')

# Inicjalizacja stanu sesji
if 'user' not in st.session_state:
    st.session_state.user = None

# Funkcja ładowania użytkowników z pliku
def load_users():
    try:
        return pd.read_excel(USERS_FILE, sheet_name='Users')
    except FileNotFoundError:
        users = pd.DataFrame({'Username': ['admin'], 'Password': ['admin'], 'Role': ['Admin']})
        users.to_excel(USERS_FILE, sheet_name='Users', index=False)
        return users

# Funkcja logowania
def login(username, password, users_df):
    user = users_df[(users_df['Username'] == username) & (users_df['Password'] == password)]
    if not user.empty:
        return user.iloc[0]
    return None

# Funkcja ładowania danych produkcyjnych
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.date
        return df
    else:
        return pd.DataFrame(columns=['Date', 'Company', 'Seal Count', 'Operator', 'Seal Type', 'Production Time', 'Downtime', 'Reason for Downtime'])

# Funkcja zapisywania danych
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# Wczytanie użytkowników i danych produkcyjnych
users_df = load_users()
df = load_data()

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
            # Formularz dodawania nowych danych produkcyjnych
    st.sidebar.header("➕ Add New Production Entry")
    with st.sidebar.form("production_form"):
        date = st.date_input("Production Date", value=datetime.date.today())
        company = st.text_input("Company Name")
        operator = st.text_input("Operator", value=st.session_state.user['Username'])
        seal_type = st.selectbox("Seal Type", ['Standard Soft', 'Standard Hard', 'Custom Soft', 'Custom Hard', 'V-Rings'])
        seals_count = st.number_input("Number of Seals", min_value=0, step=1)
        production_time = st.number_input("Production Time (Minutes)", min_value=0.0, step=0.1)
        downtime = st.number_input("Downtime (Minutes)", min_value=0.0, step=0.1)
        downtime_reason = st.text_input("Reason for Downtime")
        submitted = st.form_submit_button("Save Entry")

        if submitted:
            new_entry = {
                'Date': date,
                'Company': company,
                'Seal Count': seals_count,
                'Operator': operator,
                'Seal Type': seal_type,
                'Production Time': production_time,
                'Downtime': downtime,
                'Reason for Downtime': downtime_reason
            }
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            save_data(df)
            st.sidebar.success("Production entry saved successfully.")

    # Zakładki z danymi i wykresami
    tab1, tab2 = st.tabs(["📊 Production Data", "📈 Production Charts"])

    with tab1:
        st.header("📊 Production Data Overview")
        if not df.empty:
            st.dataframe(df)

    with tab2:
        st.header("📈 Production Charts")
        if not df.empty:
            fig = px.line(df, x='Date', y='Seal Count', title='Daily Production Trend')
            st.plotly_chart(fig)

            fig = px.bar(df, x='Company', y='Seal Count', title='Production by Company')
            st.plotly_chart(fig)

            fig = px.bar(df, x='Operator', y='Seal Count', title='Production by Operator')
            st.plotly_chart(fig)

