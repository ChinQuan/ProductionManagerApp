import streamlit as st
import plotly.express as px
import pandas as pd

def show_charts(df):
    st.header("📈 Production Charts")

    if not df.empty:
        # ✅ Konwersja kolumny 'Date' do formatu tylko daty (bez godzin)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.date

        # 📅 Dodanie możliwości filtrowania danych po dacie
        start_date = st.sidebar.date_input("Start Date", value=df['Date'].min())
        end_date = st.sidebar.date_input("End Date", value=df['Date'].max())

        # 🔥 Filtrowanie danych na podstawie wybranego zakresu dat
        filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

        # 📊 Wykres trendu dziennej produkcji
        daily_production = filtered_df.groupby('Date')['Seal Count'].sum().reset_index()
        
        fig = px.line(
            daily_production,
            x='Date',
            y='Seal Count',
            title='Daily Production Trend',
            markers=True
        )
        fig.update_layout(
            xaxis_title="Date", 
            yaxis_title="Seal Count",
            xaxis_type='category',  # ✅ Traktowanie dat jako kategorie (bez godzin)
            xaxis_tickformat='%Y-%m-%d'
        )
        st.plotly_chart(fig)

        # 📊 Wykres produkcji wg firmy
        company_production = filtered_df.groupby('Company')['Seal Count'].sum().reset_index()
        
        fig = px.bar(
            company_production,
            x='Company',
            y='Seal Count',
            title='Production by Company'
        )
        fig.update_layout(xaxis_title="Company", yaxis_title="Seal Count")
        st.plotly_chart(fig)

        # 📊 Wykres produkcji wg operatora
        operator_production = filtered_df.groupby('Operator')['Seal Count'].sum().reset_index()
        
        fig = px.bar(
            operator_production,
            x='Operator',
            y='Seal Count',
            title='Production by Operator'
        )
        fig.update_layout(xaxis_title="Operator", yaxis_title="Seal Count")
        st.plotly_chart(fig)

        # 📊 Wykres produkcji wg rodzaju uszczelek
        seal_type_production = filtered_df.groupby('Seal Type')['Seal Count'].sum().reset_index()
        
        fig = px.bar(
            seal_type_production,
            x='Seal Type',
            y='Seal Count',
            title='Production by Seal Type'
        )
        fig.update_layout(xaxis_title="Seal Type", yaxis_title="Seal Count")
        st.plotly_chart(fig)
