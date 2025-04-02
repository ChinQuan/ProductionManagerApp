import pandas as pd

# Load users data from users.xlsx
def load_users():
    try:
        return pd.read_excel('users.xlsx', sheet_name='Users')
    except FileNotFoundError:
        return pd.DataFrame(columns=['Username', 'Password', 'Role'])

users_df = load_users()

# User session management
def login(username, password):
    user = users_df[(users_df['Username'] == username) & (users_df['Password'] == password)]
    if not user.empty:
        return user.iloc[0]
    else:
        return None

def logout():
    return None
