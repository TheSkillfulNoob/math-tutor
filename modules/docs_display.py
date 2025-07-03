import streamlit as st
from google_utils import fetch_records, append_record, upload_file_to_folder
from datetime import datetime
import pandas as pd

def show_lessons_summary(lessons_df: pd.DataFrame):
    """Tab: two-column lessons & summary."""
    st.header("📚 Lessons & Key Points / Summary")
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
    st.header("📋 Other Handouts & Feedback")

    # ——— teacher view: feedback form ——
    if role == "Tutor":
        with st.form("feedback_form"):
            fb      = st.file_uploader("Upload feedback slides (PDF)", type="pdf")
            note    = st.text_area("Enter any notes for the student")
            confirm = st.form_submit_button("Confirm upload")

        if confirm:
            if not fb or not note:
                st.error("Please upload a PDF and enter comments before confirming.")
            else:
                # 1) upload into your Drive folder
                folder_id = cfg["slides_nonlesson_folder_id"]
                file_id   = upload_file_to_folder(folder_id, fb)

                # 2) build a direct-download URL
                file_link = f"https://drive.google.com/uc?export=download&id={file_id}"

                # 3) write into your feedback sheet
                append_record(
                    cfg["gsheet_id"],
                    "feedback",
                    [
                        datetime.now().strftime("%Y-%m-%d"),
                        fb.name,       # file_name
                        file_link,     # link
                        note           # comment
                    ]
                )
                st.success("✅ Feedback uploaded and recorded.")

    # ——— everyone sees the feedback list ——
    df_fb = fetch_records(cfg["gsheet_id"], "feedback")
    for _, row in df_fb.iterrows():
        st.info(
            f"**{row['file_name']}** | \n"
            f"[View]({row['link']})  \n"
            f"> {row['comment']}"
        )


def show_lessons_upload(role, cfg):
    st.header(" 📝 Upload Lesson Handouts & Summary")

    # ——— teacher view: lessons form ——
    if role == "Tutor":
        with st.form("lessons_form"):
            d       = st.date_input("Lesson Date")
            topic   = st.text_input("Topic")
            summary = st.text_area("Summary of Key Points")
            fbk     = st.text_area("Any additional Feedback")
            confirm = st.form_submit_button("Confirm upload")
        if confirm:
            if not topic or not summary:
                st.error("Topic and summary are required.")
            else:
                append_record(
                    cfg["gsheet_id"],
                    "lessons",
                    [
                        d.strftime("%Y-%m-%d"),
                        topic,
                        summary,
                        fbk
                    ]
                )
                st.success("✅ Lesson uploaded.")

def render_handouts(role, cfg):
    if role == "Tutor":
        tabs = st.tabs([
            "📝 Lessons & Summary",
            "📋 Other Handouts",
            "✏️ Upload Lesson"
        ])
        with tabs[2]:
            show_lessons_upload(role, cfg)
    else:
        tabs = st.tabs([
            "📝 Lessons & Summary",
            "📋 Other Handouts"
        ])
        
    with tabs[0]:
        df_ls = fetch_records(cfg["gsheet_id"], "lessons")
        df_fb = fetch_records(cfg["gsheet_id"], "feedback")
        show_lessons_summary(df_ls, df_fb)
    with tabs[1]:
        show_feedback(role, cfg)
    
    