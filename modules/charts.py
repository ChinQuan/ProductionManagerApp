import streamlit as st
import plotly.express as px
import pandas as pd

def show_charts(df):
    st.header("📈 Production Charts")

    if not df.empty:
        # ✅ Upewniamy się, że kolumna 'Date' jest w formacie datetime
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.date  # Usunięcie godzin, zostaje tylko data

        # 🔍 Wykres trendu dziennej produkcji
        daily_production = df.groupby('Date')['Seal Count'].sum().reset_index()
        
        fig = px.line(
            daily_production,
            x='Date',
            y='Seal Count',
            title='Daily Production Trend',
            markers=True
        )
        fig.update_layout(xaxis_title="Date", yaxis_title="Seal Count")
        st.plotly_chart(fig)

        # 🔍 Wykres produkcji wg firmy
        company_production = df.groupby('Company')['Seal Count'].sum().reset_index()
        
        fig = px.bar(
            company_production,
            x='Company',
            y='Seal Count',
            title='Production by Company'
        )
        fig.update_layout(xaxis_title="Company", yaxis_title="Seal Count")
        st.plotly_chart(fig)

        # 🔍 Wykres produkcji wg operatora
        operator_production = df.groupby('Operator')['Seal Count'].sum().reset_index()
        
        fig = px.bar(
            operator_production,
            x='Operator',
            y='Seal Count',
            title='Production by Operator'
        )
        fig.update_layout(xaxis_title="Operator", yaxis_title="Seal Count")
        st.plotly_chart(fig)

        # 🔍 Wykres produkcji wg rodzaju uszczelek
        seal_type_production = df.groupby('Seal Type')['Seal Count'].sum().reset_index()
        
        fig = px.bar(
            seal_type_production,
            x='Seal Type',
            y='Seal Count',
            title='Production by Seal Type'
        )
        fig.update_layout(xaxis_title="Seal Type", yaxis_title="Seal Count")
        st.plotly_chart(fig)
