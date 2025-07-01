import streamlit as st
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
from google.oauth2.service_account import Credentials


def _connect(sheet_key, worksheet_name):
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scopes,
    )
    client = gspread.authorize(creds)
    return client.open_by_key(sheet_key).worksheet(worksheet_name)


def fetch_records(sheet_key, ws_name):
    ws = _connect(sheet_key, ws_name)
    return pd.DataFrame(ws.get_all_records())


def push_dataframe(sheet_key, ws_name, df):
    ws = _connect(sheet_key, ws_name)
    set_with_dataframe(ws, df)