import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import bcrypt

# Konfiguracja aplikacji Streamlit
st.set_page_config(page_title="Production Manager App", layout="wide")
st.title("Production Manager App")

# Inicjalizacja stanu sesji
if 'user' not in st.session_state:
    st.session_state.user = None
# Funkcja połączenia z Google Sheets
def connect_to_gsheets(sheet_name="ProductionManagerApp", worksheet_name='Sheet1'):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"
    ]

    credentials = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials, scope)
    client = gspread.authorize(creds)

    try:
        sheet = client.open(sheet_name).worksheet(worksheet_name)
        return sheet
    except Exception as e:
        st.error(f"❌ Błąd połączenia z Google Sheets: {e}")
        return None

# Funkcja odczytu danych produkcyjnych
def load_data_from_gsheets():
    sheet = connect_to_gsheets()
    if sheet:
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    return pd.DataFrame(columns=['Date', 'Company', 'Seal Count', 'Operator', 'Seal Type', 'Production Time', 'Downtime', 'Reason for Downtime'])

# Funkcja zapisu danych produkcyjnych
def save_data_to_gsheets(dataframe):
    try:
        sheet = connect_to_gsheets()
        dataframe = dataframe.astype(str)
        sheet.clear()
        sheet.update([dataframe.columns.tolist()] + dataframe.values.tolist())
    except Exception as e:
        st.error(f"Błąd zapisu do Google Sheets: {e}")

# Funkcje obsługi użytkowników z szyfrowaniem haseł
def load_users():
    sheet = connect_to_gsheets(worksheet_name="Users")
    if sheet:
        data = sheet.get_all_records()
        if data:
            return pd.DataFrame(data)
    # domyślny admin jeśli brak danych
    hashed_pw = bcrypt.hashpw("admin".encode(), bcrypt.gensalt()).decode()
    df = pd.DataFrame({'Username': ['admin'], 'Password': [hashed_pw], 'Role': ['Admin']})
    sheet.update([df.columns.tolist()] + df.values.tolist())
    return df

# Funkcja logowania z szyfrowaniem
def login(username, password, users_df):
    user = users_df[users_df['Username'] == username]
    if not user.empty:
        stored_pw = user.iloc[0]['Password']
        if bcrypt.checkpw(password.encode(), stored_pw.encode()):
            return user.iloc[0]
    return None
# Załadowanie użytkowników i danych produkcyjnych
users_df = load_users()
df = load_data_from_gsheets()

# Logowanie użytkownika
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
    st.sidebar.success(f"✅ Logged in as {st.session_state.user['Username']}")
    if st.sidebar.button("Logout"):
        st.session_state.user = None

# Po zalogowaniu
if st.session_state.user is not None:
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
            if not company or seals_count <= 0:
                st.sidebar.error("Provide a valid company name and seal count!")
            else:
                new_entry = {
                    'Date': date, 'Company': company, 'Seal Count': seals_count,
                    'Operator': operator, 'Seal Type': seal_type,
                    'Production Time': production_time, 'Downtime': downtime,
                    'Reason for Downtime': downtime_reason
                }
                df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
                save_data_to_gsheets(df)
                st.sidebar.success("✅ Entry saved!")

    # Zakładki z danymi
    tab1, tab2 = st.tabs(["Home", "Production Charts"])

    with tab1:
        st.header("📊 Production Data Overview")
        st.dataframe(df)

    with tab2:
        st.header("📈 Production Charts")
        if not df.empty:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            fig1 = px.line(df, x='Date', y='Seal Count', title='Daily Production Trend')
            st.plotly_chart(fig1)

            fig2 = px.bar(df, x='Company', y='Seal Count', title='Production by Company')
            st.plotly_chart(fig2)

            fig3 = px.bar(df, x='Operator', y='Seal Count', title='Production by Operator')
            st.plotly_chart(fig3)

            fig4 = px.bar(df, x='Seal Type', y='Seal Count', title='Production by Seal Type')
            st.plotly_chart(fig4)

    # Panel edycji/usuwania tylko dla admina
    if st.session_state.user.get('Role') == 'Admin':
        st.sidebar.header("✏️ Edit or Delete Entry")
        if not df.empty:
            selected_index = st.sidebar.selectbox("Select Entry to Edit", df.index)
            selected_row = df.loc[selected_index]

            with st.form("edit_form"):
                date = st.date_input("Edit Date", value=pd.to_datetime(selected_row['Date']).date())
                company = st.text_input("Edit Company", selected_row['Company'])
                seals_count = st.number_input("Edit Seal Count", value=int(selected_row['Seal Count']))
                prod_time = st.number_input("Edit Production Time", value=float(selected_row['Production Time']))
                downtime = st.number_input("Edit Downtime", value=float(selected_row['Downtime']))
                downtime_reason = st.text_input("Edit Downtime Reason", selected_row['Reason for Downtime'])

                update = st.form_submit_button("Update")
                delete = st.form_submit_button("Delete")

                if update:
                    df.loc[selected_index] = [date, company, seals_count, selected_row['Operator'], selected_row['Seal Type'], prod_time, downtime, downtime_reason]
                    save_data_to_gsheets(df)
                    st.sidebar.success("✅ Updated!")

                if delete:
                    df = df.drop(selected_index).reset_index(drop=True)
                    save_data_to_gsheets(df)
                    st.sidebar.success("🗑️ Deleted!")
