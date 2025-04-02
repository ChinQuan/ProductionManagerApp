import streamlit as st
import pandas as pd
import plotly.express as px

def show_charts(df):
    st.header("📈 Enhanced Production Charts")
    
    if df.empty:
        st.write("No data available to display charts.")
        return

    # Filtrowanie danych
    operators = df['Operator'].unique().tolist()
    companies = df['Company'].unique().tolist()
    seal_types = df['Seal Type'].unique().tolist()

    selected_operator = st.selectbox("Filter by Operator", ["All"] + operators)
    selected_company = st.selectbox("Filter by Company", ["All"] + companies)
    selected_seal_type = st.selectbox("Filter by Seal Type", ["All"] + seal_types)

    filtered_df = df.copy()

    if selected_operator != "All":
        filtered_df = filtered_df[filtered_df['Operator'] == selected_operator]

    if selected_company != "All":
        filtered_df = filtered_df[filtered_df['Company'] == selected_company]

    if selected_seal_type != "All":
        filtered_df = filtered_df[filtered_df['Seal Type'] == selected_seal_type]

    # Wykresy
    fig1 = px.line(filtered_df, x='Date', y='Seal Count', title='Daily Production Trend')
    st.plotly_chart(fig1)

    fig2 = px.bar(filtered_df, x='Company', y='Seal Count', title='Production by Company')
    st.plotly_chart(fig2)
