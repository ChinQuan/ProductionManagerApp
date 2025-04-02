import streamlit as st
import pandas as pd
import datetime
import os
import plotly.express as px

# Initialize the application
st.set_page_config(page_title="Production Manager App", layout="wide")
st.title("Production Manager App")

# Get current working directory
current_dir = os.getcwd()
DATA_FILE = os.path.abspath(os.path.join(current_dir, 'Production_orders.csv'))
TEST_FILE = os.path.abspath(os.path.join(current_dir, 'test_file.txt'))

# Displaying directory information
st.sidebar.write(f"📂 Current Directory: {current_dir}")
st.sidebar.write(f"📂 Absolute Data File Path: {DATA_FILE}")

# Test if directory is writable by creating a test file
try:
    with open(TEST_FILE, 'w') as f:
        f.write('Test file creation successful.')
    st.sidebar.write("✅ Test file 'test_file.txt' created successfully.")
    os.remove(TEST_FILE)  # Delete the test file after successful creation
except Exception as e:
    st.sidebar.error(f"❌ Failed to create test file: {e}")

# Load users data from Excel without password encryption
def load_users():
    try:
        users = pd.read_excel('users.xlsx', sheet_name='Users')
        return users
    except FileNotFoundError:
        users = pd.DataFrame({'Username': ['admin'], 'Password': ['admin'], 'Role': ['Admin']})
        users.to_excel('users.xlsx', sheet_name='Users', index=False)
        return users

# Simple login logic
def login(username, password, users_df):
    user = users_df[(users_df['Username'] == username) & (users_df['Password'] == password)]
    if not user.empty:
        return user.iloc[0]
    return None

# Load production data from CSV
def load_data():
    if os.path.exists(DATA_FILE):
        st.sidebar.write("📥 Found existing file: Loading data...")
        df = pd.read_csv(DATA_FILE)
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.date
        return df
    else:
        st.sidebar.write("📄 No existing file found. Creating a new DataFrame.")
        return pd.DataFrame(columns=['Date', 'Company', 'Seal Count', 'Operator', 'Seal Type', 'Production Time', 'Downtime', 'Reason for Downtime'])

# Save data safely with absolute path
def save_data(df):
    try:
        df.to_csv(DATA_FILE, mode='w', header=True, index=False)  # Nadpisywanie pliku w trybie 'w'
        full_path = os.path.abspath(DATA_FILE)
        if os.path.exists(DATA_FILE):
            st.sidebar.write(f"✅ Data saved successfully! File path: {full_path}")
            file_content = pd.read_csv(DATA_FILE)
            st.sidebar.write("📄 Current file content:")
            st.sidebar.write(file_content)
        else:
            st.sidebar.error("❌ File was not created! Check write permissions or path.")
    except Exception as e:
        st.sidebar.error(f"❌ Error saving data: {e}")

# Load users and production data
users_df = load_users()
df = load_data()

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None

# Login panel
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

    # Sidebar Form for Adding Entries
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
    # Main Page Tabs
    tab1, tab2 = st.tabs(["Home", "Production Charts"])

    with tab1:
        st.header("📊 Production Data Overview")
        if not df.empty:
            st.dataframe(df)

            st.header("📈 Production Statistics")
            try:
                daily_average = df.groupby('Date')['Seal Count'].sum().mean()
                st.write(f"### Average Daily Production: {daily_average:.2f} seals")

                top_companies = df.groupby('Company')['Seal Count'].sum().sort_values(ascending=False).head(3)
                st.write("### Top 3 Companies by Production")
                st.write(top_companies)

                top_operators = df.groupby('Operator')['Seal Count'].sum().sort_values(ascending=False).head(3)
                st.write("### Top 3 Operators by Production")
                st.write(top_operators)
            except Exception as e:
                st.error(f"❌ Error calculating statistics: {e}")

    with tab2:
        st.header("📈 Production Charts")
        if not df.empty:
            filtered_df = df.copy()
            filtered_df['Date'] = filtered_df['Date'].astype(str)

            try:
                fig = px.line(filtered_df, x='Date', y='Seal Count', title='Daily Production Trend')
                fig.update_xaxes(type='category')
                st.plotly_chart(fig)

                fig = px.bar(filtered_df, x='Company', y='Seal Count', title='Production by Company')
                st.plotly_chart(fig)

                fig = px.bar(filtered_df, x='Operator', y='Seal Count', title='Production by Operator')
                st.plotly_chart(fig)

                fig = px.bar(filtered_df, x='Seal Type', y='Seal Count', title='Production by Seal Type')
                st.plotly_chart(fig)
            except Exception as e:
                st.error(f"❌ Error generating charts: {e}")
