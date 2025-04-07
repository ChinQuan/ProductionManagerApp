import streamlit as st
import plotly.express as px
import pandas as pd

def show_charts(df):
    st.header("📈 Production Charts")

    if not df.empty:
        # ✅ Konwersja kolumny 'Date' do formatu datetime i wyciągnięcie tylko daty
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.date

        # 📅 Opcje filtrowania
        filter_option = st.selectbox(
            "Select Data Filter",
            ["All Data", "Working Days Only (Mon-Fri)", "Order Dates Only"]
        )

        if filter_option == "Working Days Only (Mon-Fri)":
            # 🔍 Filtrowanie tylko dni roboczych (poniedziałek - piątek)
            df = df[pd.to_datetime(df['Date']).dt.dayofweek < 5]

        elif filter_option == "Order Dates Only":
            # 🔍 Usunięcie pustych lub błędnych dat
            df = df.dropna(subset=['Date'])

        # 🔍 Wykres trendu dziennej produkcji
        daily_production = df.groupby('Date')['Seal Count'].sum().reset_index()
        
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
            xaxis_type='category',
            xaxis_tickformat='%Y-%m-%d'
        )
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
