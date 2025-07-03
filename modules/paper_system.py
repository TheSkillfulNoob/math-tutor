import streamlit as st
import re
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from google_utils import fetch_records, list_subfolders, list_files

st.markdown(
    """
    <style>
      /* Question-Paper button (orange) */
      .qp-button {
        background-color: #FFA500;
        color: #ffffff;
        border: none;
        border-radius: 5px;
        padding: 8px 0;
        width: 100%;
        font-size: 16px;
        cursor: pointer;
        transition: background-color 0.2s ease;
      }
      .qp-button:hover {
        background-color: #FF8C00;
      }

      /* Marking-Scheme button (blue) */
      .ms-button {
        background-color: #007BFF;
        color: #ffffff;
        border: none;
        border-radius: 5px;
        padding: 8px 0;
        width: 100%;
        font-size: 16px;
        cursor: pointer;
        transition: background-color 0.2s ease;
      }
      .ms-button:hover {
        background-color: #0056b3;
      }
    </style>
    """,
    unsafe_allow_html=True
)

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

def _parse_mark(mark_str: str, hard_max: int):
    """
    Parse “obtained/maximum” → (obtained, maximum, pct, error_msg).
    """
    if "/" not in mark_str:
        return None, None, None, "❌ Use format “num/num”, e.g. 21/31"
    parts = mark_str.split("/")
    if len(parts) != 2:
        return None, None, None, "❌ Exactly one slash allowed"
    try:
        obt = int(parts[0].strip())
        mx  = int(parts[1].strip())
    except ValueError:
        return None, None, None, "❌ Both values must be integers"
    if mx > hard_max:
        return None, None, None, f"❌ Section max cannot exceed {hard_max}"
    if obt < 0 or obt > mx:
        return None, None, None, f"❌ Obtained must be between 0 and {mx}"
    pct = obt / mx * 100
    return obt, mx, pct, None

def _add_p1_score(config):
    st.markdown("### 📝 Tutor: Add Paper 1 Score (format “obtained/maximum”)")
    with st.form("p1_form"):
        c_date, c_set, c_a1, c_a2, c_b = st.columns(5)
        with c_date:
            d = st.date_input("Date")
        with c_set:
            set_name = st.text_input("Set Name")
        with c_a1:
            a1_str = st.text_input("A1 (max 35)", placeholder="e.g. 28/35")
        with c_a2:
            a2_str = st.text_input("A2 (max 35)", placeholder="e.g. 30/35")
        with c_b:
            b_str  = st.text_input("B (max 35)", placeholder="e.g. 25/35")
        comments = st.text_area("Comments")

        if st.form_submit_button("Submit P1"):
            # parse each
            a1_obt, a1_max, a1_pct, err1 = _parse_mark(a1_str, 35)
            a2_obt, a2_max, a2_pct, err2 = _parse_mark(a2_str, 35)
            b_obt,  b_max,  b_pct,  err3 = _parse_mark(b_str,  35)
            errs = [e for e in (err1,err2,err3) if e]
            if errs:
                for e in errs:
                    st.error(e)
                return

            # compute total % from sums of raw & max
            total_obt = a1_obt + a2_obt + b_obt
            total_max = a1_max + a2_max + b_max
            total_pct = total_obt / total_max * 100

            ws = init_worksheet("scores_p1")
            ws.append_row([
                d.strftime("%m/%d/%Y"),
                set_name,
                a1_obt, a1_max,
                a2_obt, a2_max,
                b_obt,  b_max,
                round(total_pct, 2),
                comments or ""
            ])
            st.success("✅ Paper 1 percentage recorded.")

def _add_p2_score(config):
    st.markdown("### 📝 Tutor: Add Paper 2 Score (format “obtained/maximum”)")
    with st.form("p2_form"):
        c_date, c_set, c_a, c_b = st.columns(4)
        with c_date:
            d = st.date_input("Date")
        with c_set:
            set_name = st.text_input("Set Name")
        with c_a:
            a_str = st.text_input("A (max 30)", placeholder="e.g. 24/30")
        with c_b:
            b_str = st.text_input("B (max 15)", placeholder="e.g. 12/15")
        comments = st.text_area("Comments")

        if st.form_submit_button("Submit P2"):
            a_obt, a_max, a_pct, err1 = _parse_mark(a_str, 30)
            b_obt, b_max, b_pct, err2 = _parse_mark(b_str, 15)
            errs = [e for e in (err1,err2) if e]
            if errs:
                for e in errs:
                    st.error(e)
                return

            total_obt = a_obt + b_obt
            total_max = a_max + b_max
            total_pct = total_obt / total_max * 100

            ws = init_worksheet("scores_p2")
            ws.append_row([
                d.strftime("%m/%d/%Y"),
                set_name,
                a_obt, a_max,
                b_obt, b_max,
                round(total_pct, 2),
                comments or ""
            ])
            st.success("✅ Paper 2 percentage recorded.")

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
    # st.info(sorted(subfolders.keys())) # Debug

    # 3) for each available set, list P1/P2/MS links
    for _, row in available.iterrows():
        set_name = row["idx"]
        bd = row["begin-date"].strftime("%Y-%m-%d")
        ed = row["end-date"].strftime("%Y-%m-%d")
        st.subheader(f"📄 {set_name}  ({bd} → {ed})")

        folder_id = subfolders.get(set_name)
        if not folder_id:
            st.warning(f"⚠️ Could not find Drive folder for {set_name}")
            continue

        files = list_files(folder_id)
        # 1) categorize URLs
        p1_url = p2_url = ms_url = p2ms_url = None
        p1_have_ms = False
        for f in files:
            name = f["name"]
            fid  = f["id"]
            url  = f"https://drive.google.com/uc?export=download&id={fid}"
            low  = name.lower()
            if low.startswith("p1 ") or low.startswith("p1."):
                # plain P1 paper
                if "ms" in low:
                    p1_have_ms = True
                    ms_url = url
                else:
                    p1_url = url
            elif low.startswith("p2 ") or low.startswith("p2."):
                # plain P2 paper
                if "ms" in low:
                    # P2 MS
                    p2ms_url = url
                else:
                    p2_url = url
            elif low == "ms" or low == "ms.pdf":
                # generic MS
                ms_url = url
        # 2) render as 4 columns of buttons
        col1, col2, col3, col4 = st.columns(4)
        BUTTON_QP_HTML = '<a href="{url}" target="_blank"><button style = "background-color: #FFA500; color: #ffffff; border: none; border-radius: 5px; padding: 8px 0; width: 100%; font-size: 16px; cursor: pointer; transition: background-color 0.2s ease" onmouseover="background-color: #FF8C00">{label}</button></a>'
        BUTTON_MS_HTML = '<a href="{url}" target="_blank"><button style = "background-color: #007BFF; color: #ffffff; border: none; border-radius: 5px; padding: 8px 0; width: 100%; font-size: 16px; cursor: pointer; transition: background-color 0.2s ease" onmouseover="background-color: #0056b3">{label}</button></a>'

        with col1:
            if p1_url:
                st.markdown(
                    BUTTON_QP_HTML.format(url=p1_url, label="Download P1"),
                    unsafe_allow_html=True
                )
            else:
                st.write("—")

        with col2:
            if p2_url:
                st.markdown(
                    BUTTON_QP_HTML.format(url=p2_url, label="Download P2"),
                    unsafe_allow_html=True
                )
            else:
                st.write("—")

        with col3:
            if ms_url:
                st.markdown(
                    BUTTON_MS_HTML.format(url=ms_url, label="Download P1 MS" if p1_have_ms else "Download MS (Combined)"),
                    unsafe_allow_html=True
                )
            else:
                st.write("—")

        with col4:
            # only show a separate P2 MS button if you actually found one
            if p2ms_url:
                st.markdown(
                    BUTTON_MS_HTML.format(url=p2ms_url, label="Download P2 MS"),
                    unsafe_allow_html=True
                )
            else:
                st.write("—")