import streamlit as st
import pandas as pd
import datetime

def show_admin_panel(users_df, save_data_to_gsheets, df, current_tab):
    if current_tab == "Home":  # ✅ Edycja zleceń tylko na Home!
        st.sidebar.header("✏️ Edit or Delete Orders")

        if not df.empty:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            
            selected_index = st.sidebar.selectbox("Select Order to Edit", df.index, key="admin_edit_selectbox")
            
            if selected_index is not None:
                selected_row = df.loc[selected_index]
                
                with st.form(key=f"edit_order_form_{selected_index}"):
                    selected_date = pd.to_datetime(selected_row['Date'], errors='coerce')
                    date_value = selected_date.date() if isinstance(selected_date, pd.Timestamp) else datetime.date.today()

                    date = st.date_input("Edit Production Date", value=date_value)
                    company = st.text_input("Edit Company Name", value=selected_row['Company'])
                    operator = st.text_input("Edit Operator", value=selected_row['Operator'])
                    seal_type = st.selectbox(
                        "Edit Seal Type", 
                        ['Standard Soft', 'Standard Hard', 'Custom Soft', 'Custom Hard', 'V-Rings', 'Special'], 
                        index=['Standard Soft', 'Standard Hard', 'Custom Soft', 'Custom Hard', 'V-Rings', 'Special'].index(selected_row['Seal Type'])
                    )
                    seals_count = st.number_input("Edit Number of Seals", min_value=0, value=int(selected_row['Seal Count']))
                    production_time = st.number_input("Edit Production Time (Minutes)", min_value=0.0, value=float(selected_row['Production Time']))
                    downtime = st.number_input("Edit Downtime (Minutes)", min_value=0.0, value=float(selected_row['Downtime']))
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
                        st.sidebar.success("✅ Order updated successfully!")

                    if delete_button:
                        df = df.drop(selected_index)
                        save_data_to_gsheets(df)
                        st.sidebar.success("✅ Order deleted successfully!")
