import streamlit as st
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

def _get_drive_service():
    scopes = ["https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=scopes
    )
    return build("drive", "v3", credentials=creds)

def list_subfolders(folder_id: str) -> list[dict]:
    """Return list of {id,name} for each subfolder in folder_id."""
    svc = _get_drive_service()
    q = f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
    resp = svc.files().list(q=q, fields="files(id,name)").execute()
    return resp.get("files", [])

def list_files(folder_id: str) -> list[dict]:
    """Return list of {id,name} for each file in folder_id."""
    svc = _get_drive_service()
    q = f"'{folder_id}' in parents and trashed=false"
    resp = svc.files().list(q=q, fields="files(id,name)").execute()
    return resp.get("files", [])

def _connect(sheet_name, worksheet_name):
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scopes,
    )
    client = gspread.authorize(creds)
    return client.open(sheet_name).worksheet(worksheet_name)


def fetch_records(sheet_name, ws_name):
    ws = _connect(sheet_name, ws_name)
    return pd.DataFrame(ws.get_all_records())


def push_dataframe(sheet_name, ws_name, df):
    ws = _connect(sheet_name, ws_name)
    set_with_dataframe(ws, df)
    
def append_record(sheet_name, ws_name, record: list):
    ws = _connect(sheet_name, ws_name)
    ws.append_row(record)