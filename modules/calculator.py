import streamlit as st
import pandas as pd
import datetime

def show_calculator(df):
    st.header("📅 Production Calculator")

    if df.empty:
        st.error("🚫 No production data available. Add entries first.")
        return
    
    if 'orders' not in st.session_state:
        st.session_state.orders = []

    seal_types = df['Seal Type'].unique().tolist()
    companies = df['Company'].unique().tolist()

    selected_company = st.selectbox("Select Company", companies)
    selected_seal_type = st.selectbox("Select Seal Type", seal_types)
    order_quantity = st.number_input("Order Quantity", min_value=1, step=1)

    filtered_df = df[(df['Seal Type'] == selected_seal_type) & (df['Company'] == selected_company)]

    if not filtered_df.empty:
        total_production_time = filtered_df['Production Time'].sum()
        total_seals = filtered_df['Seal Count'].sum()

        if total_seals > 0:
            average_time_per_seal = total_production_time / total_seals
            st.success(f"📈 Average Time per Seal: {average_time_per_seal:.2f} minutes")
        else:
            average_time_per_seal = 0
    else:
        average_time_per_seal = 0

    # ✅ Dodawanie pojedynczych zleceń do listy
    if st.button("Add Order to Calculation"):
        if average_time_per_seal > 0:
            st.session_state.orders.append({
                "Company": selected_company,
                "Seal Type": selected_seal_type,
                "Order Quantity": order_quantity,
                "Average Time per Seal (minutes)": average_time_per_seal
            })
            st.success(f"✅ Order '{selected_seal_type}' for '{selected_company}' added successfully!")
        else:
            st.error("⚠️ Cannot add order without valid average time.")

    # ✅ Wyświetlanie dodanych zleceń
    if st.session_state.orders:
        st.subheader("📝 Orders to Calculate")
        orders_df = pd.DataFrame(st.session_state.orders)
        st.table(orders_df)

        if st.button("Clear All Orders"):
            st.session_state.orders = []
            st.warning("📋 All orders have been cleared.")

    # ✅ Importowanie zleceń z Excela
    st.subheader("📥 Import Orders from Excel")
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "xls"])

    if uploaded_file is not None:
        try:
            imported_df = pd.read_excel(uploaded_file)

            if all(column in imported_df.columns for column in ['Company', 'Seal Type', 'Seal Count']):
                st.write("✅ File successfully uploaded. Preview:")
                st.dataframe(imported_df)
                
                # Wyciągamy średnie czasy produkcji z dostępnych danych
                averages = df.groupby('Seal Type')['Production Time'].sum() / df.groupby('Seal Type')['Seal Count'].sum()

                imported_df['Average Time per Seal (minutes)'] = imported_df['Seal Type'].apply(lambda x: averages.get(x, None))
                imported_df.dropna(subset=['Average Time per Seal (minutes)'], inplace=True)
                
                imported_df['Total Time (minutes)'] = imported_df['Seal Count'] * imported_df['Average Time per Seal (minutes)']
                
                st.write("📈 Orders with calculated times:")
                st.dataframe(imported_df[['Company', 'Seal Type', 'Seal Count', 'Average Time per Seal (minutes)', 'Total Time (minutes)']])
                
                total_minutes = imported_df['Total Time (minutes)'].sum()
                st.success(f"✅ Total estimated time for all imported orders: {total_minutes:.2f} minutes.")
                
                # Dodawanie zaimportowanych zleceń do sesji
                for _, row in imported_df.iterrows():
                    st.session_state.orders.append({
                        "Company": row['Company'],
                        "Seal Type": row['Seal Type'],
                        "Order Quantity": row['Seal Count'],
                        "Average Time per Seal (minutes)": row['Average Time per Seal (minutes)']
                    })
                
            else:
                st.error("❌ The file must contain the columns: 'Company', 'Seal Type', 'Seal Count'")
        
        except Exception as e:
            st.error(f"❌ Error reading the file: {e}")

    # ✅ Obliczanie całkowitego czasu po kliknięciu przycisku
    if st.button("Calculate Total Time"):
        if st.session_state.orders:
            total_time = sum(order["Order Quantity"] * order["Average Time per Seal (minutes)"] for order in st.session_state.orders)
            st.success(f"✅ Total Estimated Production Time: {total_time:.2f} minutes")
        else:
            st.error("⚠️ No orders to calculate.")
