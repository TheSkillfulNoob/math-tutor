import streamlit as st
from google_utils import fetch_records, append_record
from datetime import datetime

def render(role, cfg):
    st.header("Official Documents & Feedback")

    # ——— teacher view: upload a PDF and push metadata to “feedback” sheet ——
    if role == "Tutor":
        fb = st.file_uploader("Upload feedback slides (PDF)", type="pdf")
        comment = st.text_area("Enter any notes for the student")
        if fb and comment:
            # 1) upload to your Drive folder however you do that
            #    (e.g. use Drive API / PyDrive – omitted for brevity)
            file_link = f"https://drive.google.com/…/{fb.name}"
            # 2) record into a “feedback” sheet
            append_record(
              cfg["gsheet_id"],
              "feedback",
              [datetime.now().strftime("%m/%d/%Y"), fb.name, file_link, comment]
            )
            st.success("Feedback recorded.")

    # ——— everyone sees the feedback list ——
    df_fb = fetch_records("Math-tutor", "feedback")
    for _, row in df_fb.iterrows():
        st.info(
          f"**{row['file_name']}**  \n"
          f"[View]({row['link']})  \n"
          f"> {row['comment']}"
        )