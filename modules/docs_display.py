import streamlit as st
from google_utils import fetch_records, append_record
from datetime import datetime
import pandas as pd

def show_lessons_summary(lessons_df: pd.DataFrame, feedback_df: pd.DataFrame):
    """Tab: two-column lessons & summary."""
    st.header("📝 Lessons & Key Points / Summary")
    for _, r in lessons_df.sort_values("Date", ascending=False).iterrows():
        col1, col2 = st.columns([0.4, 0.6])
        with col1:
            st.subheader(f"{r['Date']}")
            st.markdown(f"**{r['Topic']}**")
            st.write(r["Summary"])
        with col2:
            st.subheader("Resources/ Reminders")
            st.markdown("TODO implement: Slides and Exercises")
            st.write(r["Feedback"])
        st.markdown("---")

def show_feedback(role, cfg):
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

def render_handouts(
    role, cfg,
    lessons_df: pd.DataFrame,
    summary_df: pd.DataFrame
    ):
    tabs = st.tabs([
        "📋 Official Info and Other Handouts",
        "📝 Lessons & Summary"
    ])
    with tabs[0]:
        show_feedback(role, cfg)
    with tabs[1]:
        show_lessons_summary(lessons_df, summary_df)