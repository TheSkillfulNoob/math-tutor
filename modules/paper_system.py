import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

def init_gsheets(config):
    scopes = ["https://www.googleapis.com/auth/spreadsheets",
              "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file("path/to/creds.json", scopes=scopes)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(config['gsheet_id']).sheet1
    return sheet

def render(role, config):
    st.header("Exercises & Exercises Upload")

    # Fetch to-dos from Google Sheets
    sheet = init_gsheets(config)
    df = pd.DataFrame(sheet.get_all_records())
    st.table(df[['task', 'deadline', 'status']])

    # PDF upload
    if role == 'Tutor':
        st.file_uploader("Upload new PDF", type=['pdf'], help="Max 10MB")
    else: # role = "Tutee"
        # tutee view / download
        # list files from Drive folder and allow download
        pass