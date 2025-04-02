import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

def show_charts(df):
    st.header("Production Charts")
    
    # Daily production trend
    fig, ax = plt.subplots(figsize=(6, 4))
    daily_trend = df.groupby('Date')['Seal Count'].sum().reset_index()
    sns.lineplot(x='Date', y='Seal Count', data=daily_trend, ax=ax)
    ax.set_title("Daily Production Trend")
    st.pyplot(fig)

    # Production by Company
    fig, ax = plt.subplots(figsize=(6, 4))
    company_trend = df.groupby('Company')['Seal Count'].sum().reset_index()
    sns.barplot(x='Company', y='Seal Count', data=company_trend, ax=ax)
    ax.set_title("Production by Company")
    st.pyplot(fig)

    # Production by Seal Type
    fig, ax = plt.subplots(figsize=(6, 4))
    seal_type_trend = df.groupby('Seal Type')['Seal Count'].sum().reset_index()
    sns.barplot(x='Seal Type', y='Seal Count', data=seal_type_trend, ax=ax)
    ax.set_title("Production by Seal Type")
    st.pyplot(fig)

    # Production by Operator
    fig, ax = plt.subplots(figsize=(6, 4))
    operator_trend = df.groupby('Operator')['Seal Count'].sum().reset_index()
    sns.barplot(x='Operator', y='Seal Count', data=operator_trend, ax=ax)
    ax.set_title("Production by Operator")
    st.pyplot(fig)
