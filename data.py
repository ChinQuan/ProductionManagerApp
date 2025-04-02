import pandas as pd
import os

# Load production data from CSV
def load_data():
    try:
        return pd.read_csv('production_data.csv')
    except FileNotFoundError:
        return pd.DataFrame(columns=['Date', 'Company', 'Seal Count', 'Operator', 'Seal Type', 'Production Time', 'Downtime', 'Reason for Downtime'])

# Save data to CSV
def save_data(df):
    df.to_csv('production_data.csv', index=False)
