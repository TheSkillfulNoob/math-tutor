import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from google_utils import fetch_records, list_subfolders, list_files

def init_worksheet(sheet_name: str):
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=scopes
    )
    client = gspread.authorize(creds)
    return client.open("Math-tutor").worksheet(sheet_name)

def render(role: str, config: dict):
    st.header("Exercises & Paper Downloads")
    # ─ Tutor entry forms ─
    if role.lower() == "tutor":
        _add_p1_score(config)
        _add_p2_score(config)
    if role.lower() == "tutee":
        _show_available_papers(config)

def _add_p1_score(config):
    st.markdown("### 📝 Tutor: Add Paper 1 Score")
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
            ws = init_worksheet("scores_p1")
            ws.append_row([
                d.strftime("%m/%d/%Y"),
                set_name,
                a1, a2, b,
                total,
                comments or ""
            ])
            st.success("✅ Paper 1 score recorded.")

def _add_p2_score(config):
    st.markdown("### 📝 Tutor: Add Paper 2 Score")
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
            ws = init_worksheet("scores_p2")
            ws.append_row([
                d.strftime("%m/%d/%Y"),
                set_name,
                a, b,
                total,
                comments or ""
            ])
            st.success("✅ Paper 2 score recorded.")

def _show_available_papers(config):
    # 1) pull the control sheet
    df = fetch_records("Math-tutor", "paper-control")
    df["begin-date"] = pd.to_datetime(df["begin-date"])
    df["end-date"]   = pd.to_datetime(df["end-date"])
    today = pd.Timestamp.today().normalize()

    available = df[
        (df["begin-date"] <= today) &
        (today <= df["end-date"])
    ]

    if available.empty:
        st.info("No mock papers are available right now.")
        return

    # 2) map mock-selection subfolders
    root_id    = config["mock_selection_folder_id"]
    subfolders = {f["name"]: f["id"] for f in list_subfolders(root_id)}
    st.info(subfolders)

    # 3) for each available set, list P1/P2/MS links
    for _, row in available.iterrows():
        set_name = row["paper-set"]
        bd = row["begin-date"].strftime("%Y-%m-%d")
        ed = row["end-date"].strftime("%Y-%m-%d")
        st.subheader(f"{set_name}  ({bd} → {ed})")

        folder_id = subfolders.get(set_name)
        if not folder_id:
            st.warning(f"⚠️ Could not find Drive folder for {set_name}")
            continue

        files = list_files(folder_id)
        # quick‐and‐dirty grouping by prefix
        for f in files:
            name = f["name"]
            fid  = f["id"]
            url  = f"https://drive.google.com/uc?export=download&id={fid}"

            low = name.lower()
            if low.startswith("p1"):
                st.markdown(f"- [Download {name}]({url})")
            elif low.startswith("p2"):
                st.markdown(f"- [Download {name}]({url})")
            elif "ms" in low:
                st.markdown(f"- [Download Marking Scheme - {name}]({url})")
