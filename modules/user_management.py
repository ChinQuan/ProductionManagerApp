import streamlit as st
import pandas as pd

def show_user_management(users_df, save_users_to_gsheets):
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

