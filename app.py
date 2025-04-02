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

    credentials = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials, scope)
    client = gspread.authorize(creds)
    
    return client

# Funkcja ładowania danych użytkowników z Google Sheets
def load_users():
    client = connect_to_gsheets()
    try:
        sheet = client.open("ProductionManagerApp").worksheet("Users")  # Arkusz z użytkownikami
        data = sheet.get_all_records()
        if data:
            return pd.DataFrame(data)
    except Exception as e:
        st.error(f"❌ Błąd podczas ładowania użytkowników: {e}")
    return pd.DataFrame(columns=['Username', 'Password', 'Role'])

# Funkcja zapisywania użytkowników do Google Sheets
def save_users_to_gsheets(users_df):
    client = connect_to_gsheets()
    sheet = client.open("ProductionManagerApp").worksheet("Users")
    users_df = users_df.astype(str)
    sheet.clear()
    sheet.update([users_df.columns.values.tolist()] + users_df.values.tolist())

# Funkcja ładowania danych produkcyjnych z arkusza Google Sheets
def load_data_from_gsheets():
    client = connect_to_gsheets()
    try:
        sheet = client.open("ProductionManagerApp").sheet1
        data = sheet.get_all_records()
        if data:
            return pd.DataFrame(data)
    except Exception as e:
        st.error(f"❌ Błąd podczas ładowania danych produkcyjnych: {e}")
    return pd.DataFrame(columns=['Date', 'Company', 'Seal Count', 'Operator', 'Seal Type', 'Production Time', 'Downtime', 'Reason for Downtime'])

# Funkcja zapisywania danych produkcyjnych do Google Sheets
def save_data_to_gsheets(dataframe):
    client = connect_to_gsheets()
    sheet = client.open("ProductionManagerApp").sheet1
    dataframe = dataframe.astype(str)
    sheet.clear()
    sheet.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())

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
if st.session_state.user is not None:
    # Zakładki
    tab1, tab2, tab3 = st.tabs(["Home", "Production Charts", "User Management"])

    with tab1:
        st.header("📊 Production Data Overview")
        if not df.empty:
            st.dataframe(df)

    with tab2:
        st.header("📈 Production Charts")
        if not df.empty:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            fig = px.line(df, x='Date', y='Seal Count', title='Daily Production Trend')
            st.plotly_chart(fig)

            fig2 = px.bar(df, x='Company', y='Seal Count', title='Production by Company')
            st.plotly_chart(fig2)

            fig3 = px.bar(df, x='Operator', y='Seal Count', title='Production by Operator')
            st.plotly_chart(fig3)

            fig4 = px.bar(df, x='Seal Type', y='Seal Count', title='Production by Seal Type')
            st.plotly_chart(fig4)

    with tab3:
        if st.session_state.user['Role'] == 'Admin':
            st.header("👥 User Management")

            if not users_df.empty:
                st.dataframe(users_df)

            st.subheader("Add New User")
            with st.form("add_user_form"):
                new_username = st.text_input("New Username")
                new_password = st.text_input("New Password")
                new_role = st.selectbox("Role", ["Admin", "Operator"])
                add_user_btn = st.form_submit_button("Add User")

            if add_user_btn:
                new_user = pd.DataFrame([[new_username, new_password, new_role]], columns=['Username', 'Password', 'Role'])
                users_df = pd.concat([users_df, new_user], ignore_index=True)
                save_users_to_gsheets(users_df)
                st.success("User added successfully!")

            st.subheader("Delete User")
            if not users_df.empty:
                user_to_delete = st.selectbox("Select User to Delete", users_df['Username'])
                if st.button("Delete User"):
                    users_df = users_df[users_df['Username'] != user_to_delete]
                    save_users_to_gsheets(users_df)
                    st.success("User deleted successfully!")

    # ✅ Opcja edytowania i usuwania zleceń dostępna tylko dla Admina
    if st.session_state.user['Role'] == 'Admin':
        st.sidebar.header("✏️ Edit or Delete Orders")

        if not df.empty:
            selected_index = st.sidebar.selectbox("Select Order to Edit", df.index)
            
            if selected_index is not None:
                selected_row = df.loc[selected_index]
                
                with st.form("edit_order_form"):
                    date = st.date_input("Edit Production Date", value=pd.to_datetime(selected_row['Date']).date())
                    company = st.text_input("Edit Company Name", value=selected_row['Company'])
                    operator = st.text_input("Edit Operator", value=selected_row['Operator'])
                    seal_type = st.selectbox("Edit Seal Type", ['Standard Soft', 'Standard Hard', 'Custom Soft', 'Custom Hard', 'V-Rings'], index=['Standard Soft', 'Standard Hard', 'Custom Soft', 'Custom Hard', 'V-Rings'].index(selected_row['Seal Type']))
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
                        st.sidebar.success("Order updated successfully!")

                    if delete_button:
                        df = df.drop(selected_index)
                        save_data_to_gsheets(df)
                        st.sidebar.success("Order deleted successfully!")
