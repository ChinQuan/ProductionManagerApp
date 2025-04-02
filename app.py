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

# Konfiguracja aplikacji
st.set_page_config(page_title="Production Manager App", layout="wide")
st.title("Production Manager App")

# Inicjalizacja stanu sesji
if 'user' not in st.session_state:
    st.session_state.user = None

# ✅ Wczytywanie danych tylko raz do pamięci (używając cache)
@st.cache_data
def load_data_from_gsheets():
    client = connect_to_gsheets()
    sheet = client.open("ProductionManagerApp").sheet1
    data = sheet.get_all_records()
    return pd.DataFrame(data)

# ✅ Przechowywanie danych w sesji dla lepszego dostępu
if 'data' not in st.session_state:
    st.session_state.data = load_data_from_gsheets()
df = st.session_state.data  # Używamy danych z pamięci

# ✅ Funkcja połączenia z Google Sheets
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

# ✅ Funkcja zapisywania danych produkcyjnych do Google Sheets (Tylko przy zmianach)
def save_data_to_gsheets(dataframe):
    client = connect_to_gsheets()
    sheet = client.open("ProductionManagerApp").sheet1
    
    dataframe['Date'] = dataframe['Date'].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) else None)
    dataframe = dataframe.astype(str)
    sheet.clear()
    sheet.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())
    st.session_state.data = dataframe  # Aktualizacja pamięci

# ✅ Funkcja logowania
def login(username, password, users_df):
    user = users_df[(users_df['Username'] == username) & (users_df['Password'] == password)]
    if not user.empty:
        return user.iloc[0]
    return None
# Wczytanie użytkowników z Google Sheets
@st.cache_data
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

# Wczytywanie użytkowników do sesji
if 'users' not in st.session_state:
    st.session_state.users = load_users()
users_df = st.session_state.users

# ✅ Konwersja kolumny 'Date' do datetime przy starcie aplikacji
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

# ✅ Paginacja danych w tabeli (Wyświetlanie po 20 rekordów)
def paginate_dataframe(dataframe, page_size=20):
    total_pages = (len(dataframe) - 1) // page_size + 1
    page_number = st.sidebar.number_input('Page Number', min_value=1, max_value=total_pages, value=1)
    start_idx = (page_number - 1) * page_size
    end_idx = start_idx + page_size
    return dataframe.iloc[start_idx:end_idx]

# Zakładki
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Home", "Production Charts", "User Management", "Reports", "Backup", "Average Production Time"
])

with tab1:
    st.header("📊 Production Data Overview")
    
    if not df.empty:
        # 📈 Obliczanie średniej produkcji dziennej
        total_seals = df['Seal Count'].sum()
        total_days = (df['Date'].max() - df['Date'].min()).days + 1
        
        if total_days > 0:
            average_daily_production = total_seals / total_days
        else:
            average_daily_production = 0

        st.metric(label="📈 Average Daily Production", value=f"{average_daily_production:.2f} seals per day")

        # 🔥 Wyświetlanie danych z paginacją
        paginated_df = paginate_dataframe(df)
        st.dataframe(paginated_df)

    # 🔥 Automatyczne odświeżanie danych po zapisie (odczyt z pamięci)
    df = st.session_state.data
# Formularz dodawania nowych wpisów
if st.session_state.user is not None:
    st.sidebar.header("➕ Add New Order")

    with st.sidebar.form("production_form"):
        date = st.date_input("Production Date", value=datetime.date.today())
        company = st.text_input("Company Name")
        operator = st.text_input("Operator", value=st.session_state.user['Username'])
        seal_type = st.selectbox("Seal Type", ['Standard Soft', 'Standard Hard', 'Custom Soft', 'Custom Hard', 'V-Rings', 'Special'])
        seals_count = st.number_input("Number of Seals", min_value=0, step=1)
        production_time = st.number_input("Production Time (Minutes)", min_value=0.0, step=0.1)
        downtime = st.number_input("Downtime (Minutes)", min_value=0.0, step=0.1)
        downtime_reason = st.text_input("Reason for Downtime")
        submitted = st.form_submit_button("Save Order")

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
            save_data_to_gsheets(df)
            st.session_state.data = df  # Aktualizacja danych w pamięci
            st.sidebar.success("Order saved successfully!")

# ✅ Opcja edytowania i usuwania zleceń dostępna tylko dla Admina
if st.session_state.user is not None and st.session_state.user['Role'] == 'Admin':
    st.sidebar.header("✏️ Edit or Delete Orders")

    if not df.empty:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        selected_index = st.sidebar.selectbox("Select Order to Edit", df.index)
        
        if selected_index is not None:
            selected_row = df.loc[selected_index]
            
            with st.form("edit_order_form"):
                selected_date = pd.to_datetime(selected_row['Date'], errors='coerce')
                if isinstance(selected_date, pd.Timestamp):
                    date_value = selected_date.date()
                else:
                    date_value = datetime.date.today()

                date = st.date_input("Edit Production Date", value=date_value)
                company = st.text_input("Edit Company Name", value=selected_row['Company'])
                operator = st.text_input("Edit Operator", value=selected_row['Operator'])
                seal_type = st.selectbox(
                    "Edit Seal Type", 
                    ['Standard Soft', 'Standard Hard', 'Custom Soft', 'Custom Hard', 'V-Rings', 'Special'], 
                    index=['Standard Soft', 'Standard Hard', 'Custom Soft', 'Custom Hard', 'V-Rings', 'Special'].index(selected_row['Seal Type'])
                )
                seals_count = st.number_input("Edit Number of Seals", min_value=0, value=int(selected_row['Seal Count']))
                production_time = st.number_input("Edit Production Time (Minutes)", min_value=0.0, step=0.1, value=float(selected_row['Production Time']))
                downtime = st.number_input("Edit Downtime (Minutes)", min_value=0.0, step=0.1, value=float(selected_row['Downtime']))
                downtime_reason = st.text_input("Edit Reason for Downtime", value=selected_row['Reason for Downtime'])

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
                    df.at[selected_index, 'Reason for Downtime'] = downtime_reason
                    save_data_to_gsheets(df)
                    st.session_state.data = df  # Aktualizacja danych w pamięci
                    st.sidebar.success("Order updated successfully!")

                if delete_button:
                    df = df.drop(selected_index)
                    save_data_to_gsheets(df)
                    st.session_state.data = df  # Aktualizacja danych w pamięci
                    st.sidebar.success("Order deleted successfully!")
