import streamlit as st
import pandas as pd
import os
import datetime
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials

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

    # Pobieranie danych z secrets.toml
    credentials = st.secrets["gcp_service_account"]
    
    # Konfiguracja poświadczeń
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials, scope)
    client = gspread.authorize(creds)

    # Otwieranie arkusza Google (upewnij się, że nazwa arkusza jest poprawna!)
    try:
        sheet = client.open("ProductionManagerApp").sheet1  # Podaj dokładną nazwę swojego arkusza
        return sheet
    except Exception as e:
        st.error(f"❌ Błąd podczas łączenia z arkuszem Google: {e}")
        return None

# Funkcja zapisywania danych do Google Sheets
def save_data_to_gsheets(dataframe):
    sheet = connect_to_gsheets()
    if sheet:
        dataframe = dataframe.astype(str)
        sheet.clear()
        sheet.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())

# Funkcja ładowania danych z Google Sheets
def load_data_from_gsheets():
    sheet = connect_to_gsheets()
    if sheet:
        data = sheet.get_all_records()
        if data:
            return pd.DataFrame(data)
    return pd.DataFrame(columns=['Date', 'Company', 'Seal Count', 'Operator', 'Seal Type', 'Production Time', 'Downtime', 'Reason for Downtime'])

# Funkcja ładowania użytkowników
def load_users():
    try:
        return pd.read_excel('users.xlsx', sheet_name='Users')
    except FileNotFoundError:
        users = pd.DataFrame({'Username': ['admin'], 'Password': ['admin'], 'Role': ['Admin']})
        users.to_excel('users.xlsx', sheet_name='Users', index=False)
        return users

# Funkcja logowania
def login(username, password, users_df):
    user = users_df[(users_df['Username'] == username) & (users_df['Password'] == password)]
    if not user.empty:
        return user.iloc[0]
    return None

# Wczytanie użytkowników i danych produkcyjnych
users_df = load_users()
df = load_data_from_gsheets()

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
    with st.sidebar.form("production_form"):
        date = st.date_input("Production Date", value=datetime.date.today())
        company = st.text_input("Company Name")
        
        if 'user' in st.session_state and st.session_state.user is not None:
            operator_name = st.session_state.user['Username']
        else:
            operator_name = ""  # Jeśli użytkownik nie jest zalogowany
        
        operator = st.text_input("Operator", value=operator_name)
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
            save_data_to_gsheets(df)
            st.sidebar.success("Production entry saved successfully!")

    # Sprawdzamy poprawnie, czy user istnieje i jest Adminem
    if 'user' in st.session_state and st.session_state.user is not None and st.session_state.user['Role'] == 'Admin':
        st.sidebar.header("✏️ Edit or Delete Entry")

        if not df.empty:
            selected_index = st.sidebar.selectbox("Select Entry to Edit", df.index)
            
            if selected_index is not None:
                selected_row = df.loc[selected_index]
                
                with st.form("edit_form"):
                    date = st.date_input("Edit Production Date", value=pd.to_datetime(selected_row['Date']).date())
                    company = st.text_input("Edit Company Name", value=selected_row['Company'])
                    seals_count = st.number_input("Edit Number of Seals", min_value=0, value=int(selected_row['Seal Count']))
                    production_time = st.number_input("Edit Production Time (Minutes)", min_value=0.0, step=0.1, value=float(selected_row['Production Time']))
                    downtime = st.number_input("Edit Downtime (Minutes)", min_value=0.0, step=0.1, value=float(selected_row['Downtime']))
                    downtime_reason = st.text_input("Edit Reason for Downtime", value=selected_row['Reason for Downtime'])

                    update_button = st.form_submit_button("Update Entry")
                    delete_button = st.form_submit_button("Delete Entry")

                    if update_button:
                        df.at[selected_index, 'Date'] = date
                        df.at[selected_index, 'Company'] = company
                        df.at[selected_index, 'Seal Count'] = seals_count
                        df.at[selected_index, 'Production Time'] = production_time
                        df.at[selected_index, 'Downtime'] = downtime
                        df.at[selected_index, 'Reason for Downtime'] = downtime_reason
                        save_data_to_gsheets(df)
                        st.success("Entry updated successfully!")

                    if delete_button:
                        df = df.drop(selected_index)
                        save_data_to_gsheets(df)
                        st.success("Entry deleted successfully!")
