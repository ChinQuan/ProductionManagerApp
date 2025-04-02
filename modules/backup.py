import streamlit as st
import pandas as pd
from datetime import datetime

def show_backup_option(df, save_data_to_gsheets):
    st.header("💾 Backup and Restore")

    # Tworzenie backupu
    if st.button("Create Backup"):
        backup_filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(label="Download Backup", data=csv_data, file_name=backup_filename, mime="text/csv")
        st.success("Backup created successfully!")

    # Przywracanie z backupu
    uploaded_file = st.file_uploader("Upload Backup File", type="csv")
    if uploaded_file is not None:
        backup_df = pd.read_csv(uploaded_file)
        save_data_to_gsheets(backup_df)
        st.success("Backup restored successfully!")
