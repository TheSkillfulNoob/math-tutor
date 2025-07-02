import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

def init_worksheet(config, sheet_name: str):
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=scopes
    )
    client = gspread.authorize(creds)
    return client.open_by_key(config["Math-tutor"]).worksheet(sheet_name)

def render(role: str, config: dict):
    st.header("Exercises & Paper Scores")

    # … your to-do list / PDF code here …

    # ─ Tutor entry forms ─
    if role.lower() == "tutor":
        _add_p1_score(config)
        _add_p2_score(config)

def _add_p1_score(config):
    st.markdown("### 📝 Add Paper 1 Score")
    with st.form("p1_form"):
        cols = st.columns(5)
        with cols[0]:
            d = st.date_input("Date")
        with cols[1]:
            set_name = st.text_input("Set Name")
        with cols[2]:
            a1 = st.number_input("A1 (max 35)", min_value=0, max_value=35, step=1)
        with cols[3]:
            a2 = st.number_input("A2 (max 35)", min_value=0, max_value=35, step=1)
        with cols[4]:
            b  = st.number_input("B  (max 35)", min_value=0, max_value=35, step=1)
        comments = st.text_area("Comments")
        if st.form_submit_button("Submit P1"):
            total = a1 + a2 + b
            ws = init_worksheet(config, "scores_p1")
            ws.append_row([
                d.isoformat(),
                set_name,
                a1, a2, b,
                total,
                comments or ""
            ])
            st.success("✅ Paper 1 score recorded.")

def _add_p2_score(config):
    st.markdown("### 📝 Add Paper 2 Score")
    with st.form("p2_form"):
        cols = st.columns(4)
        with cols[0]:
            d = st.date_input("Date")
        with cols[1]:
            set_name = st.text_input("Set Name")
        with cols[2]:
            a = st.number_input("A (max 30)", min_value=0, max_value=30, step=1)
        with cols[3]:
            b = st.number_input("B (max 15)", min_value=0, max_value=15, step=1)
        comments = st.text_area("Comments")
        if st.form_submit_button("Submit P2"):
            total = a + b
            ws = init_worksheet(config, "scores_p2")
            ws.append_row([
                d.isoformat(),
                set_name,
                a, b,
                total,
                comments or ""
            ])
            st.success("✅ Paper 2 score recorded.")
