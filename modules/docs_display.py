import streamlit as st
from datetime import datetime
from google_utils import fetch_records, append_record, upload_file_to_folder

def show_lessons(role, cfg):
    """Display existing lessons & allow Tutor to upload Lecture + Exercise files."""
    st.header("📚 Lessons & Resources")

    # ─── Tutor upload form ───
    if role == "Tutor":
        with st.form("lessons_form"):
            col_date_content = st.columns([0.3, 0.7])
            with col_date_content[0]:
                d         = st.date_input("Lesson Date")
                topic     = st.text_input("Topic")
            with col_date_content[1]:
                summary   = st.text_area("Summary of Key Points")
            
            col_handout_content = st.columns([0.5, 0.5])
            with col_handout_content[0]:
                lec_notes = st.text_area("Lecture Notes Description")
                lec_file  = st.file_uploader("Upload Lecture PDF", type="pdf")
            with col_handout_content[1]:
                ex_notes  = st.text_area("Exercise Notes Description")
                ex_file   = st.file_uploader("Upload Exercise PDF", type="pdf")
            confirm   = st.form_submit_button("Confirm upload")

        if confirm:
            errs = []
            if not topic:    errs.append("Topic is required.")
            if not summary:  errs.append("Summary is required.")
            if not lec_file: errs.append("Lecture PDF is required.")
            if not ex_file:  errs.append("Exercise PDF is required.")
            if errs:
                for e in errs:
                    st.error(e)
            else:
                # 1) upload both files into your Drive folder
                folder_id   = cfg["slides_lessons_folder_id"]
                lec_id      = upload_file_to_folder(folder_id, lec_file)
                ex_id       = upload_file_to_folder(folder_id, ex_file)
                lec_link    = f"https://drive.google.com/uc?export=download&id={lec_id}"
                ex_link     = f"https://drive.google.com/uc?export=download&id={ex_id}"

                # 2) append a row to the `lessons` sheet
                append_record(
                    cfg["gsheet_id"],
                    "lessons",
                    [
                        d.strftime("%Y-%m-%d"),
                        topic,
                        summary,
                        lec_notes,
                        lec_link,
                        ex_notes,
                        ex_link
                    ]
                )
                st.success("✅ Lesson & exercise uploaded.")

    # ─── Display existing lessons ───
    df_ls = fetch_records(cfg["gsheet_id"], "lessons")  # :contentReference[oaicite:0]{index=0}
    for _, row in df_ls.sort_values("Date", ascending=False).iterrows():
        col1, col2 = st.columns([0.5, 0.5])
        with col1:
            st.subheader(f"{row['Date']} — {row['Topic']}")
            st.write(row["Summary"])
        with col2:
            st.markdown("**Lecture Notes**")
            st.write(row["Lec_notes"])
            st.markdown(f"[Download Lecture PDF]({row['Lec_link']})")
            st.markdown("**Exercise**")
            st.write(row["Ex_notes"])
            st.markdown(f"[Download Exercise PDF]({row['Ex_link']})")
        st.markdown("---")


def show_feedback(role, cfg):
    """Unchanged feedback uploader/display (for non-lesson handouts)."""
    st.header("📋 Other Handouts & Feedback")

    if role == "Tutor":
        with st.form("feedback_form"):
            fb      = st.file_uploader("Upload feedback slides (PDF)", type="pdf")
            note    = st.text_area("Enter any notes for the student")
            confirm = st.form_submit_button("Confirm upload")

        if confirm:
            if not fb or not note:
                st.error("Please upload a PDF and enter comments before confirming.")
            else:
                folder_id = cfg["slides_nonlesson_folder_id"]
                file_id   = upload_file_to_folder(folder_id, fb)
                link      = f"https://drive.google.com/uc?export=download&id={file_id}"
                append_record(
                    cfg["gsheet_id"],
                    "feedback",
                    [ datetime.now().strftime("%Y-%m-%d"), fb.name, link, note ]
                )
                st.success("✅ Feedback uploaded and recorded.")

    df_fb = fetch_records(cfg["gsheet_id"], "feedback")
    for _, row in df_fb.iterrows():
        st.info(
            f"**{row['file_name']}**  \n"
            f"[Download]({row['link']})  \n"
            f"> {row['comment']}"
        )


def render_handouts(role, cfg):
    """Top‐level tab layout for docs & lessons."""
    tabs = ["📚 Lessons & Resources", "📋 Other Handouts"]
    if role == "Tutor":
        tabs.append("✏️ Upload Lesson & Exercise")

    ui_tabs = st.tabs(tabs)

    with ui_tabs[0]:
        show_lessons(role, cfg)
    with ui_tabs[1]:
        show_feedback(role, cfg)
    if role == "Tutor":
        with ui_tabs[2]:
            # same lessons form appears here for clarity
            show_lessons(role, cfg)

    
    