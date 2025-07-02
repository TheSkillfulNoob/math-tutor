import streamlit as st
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
from google.oauth2.service_account import Credentials
from pydrive2.auth import GoogleAuth, ServiceAccountCredentials
from pydrive2.drive import GoogleDrive

def _init_drive():
    # 1) build a GoogleAuth set up for service‐account
    gauth = GoogleAuth()
    gauth.auth_method = "service"
    gauth.credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    return GoogleDrive(gauth)

def list_subfolders(folder_id: str):
    drive = _init_drive()
    q = f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
    files = drive.ListFile({'q': q}).GetList()
    return [{"id":f["id"], "name":f["title"]} for f in files]

def list_files(folder_id: str):
    drive = _init_drive()
    q = f"'{folder_id}' in parents and trashed=false"
    files = drive.ListFile({'q': q}).GetList()
    return [{"id":f["id"], "name":f["title"]} for f in files]

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