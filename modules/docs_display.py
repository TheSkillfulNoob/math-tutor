import streamlit as st
from datetime import datetime
from google_utils import fetch_records, append_record, upload_file_to_folder

def display_lessons(cfg):
    """Display existing lessons & resources."""
    df_ls = fetch_records(cfg["gsheet_id"], "lessons")
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

def upload_lessons(role, cfg):
    """Tutor-only form to upload lessons + exercise PDFs."""
    if role.lower() != "tutor":
        return
    with st.form("lessons_upload_form"):
        d         = st.date_input("Lesson Date")
        topic     = st.text_input("Topic")
        summary   = st.text_area("Summary of Key Points")
        lec_notes = st.text_area("Lecture Notes Description")
        lec_file  = st.file_uploader("Upload Lecture PDF", type="pdf", key="lec_up")
        ex_notes  = st.text_area("Exercise Notes Description")
        ex_file   = st.file_uploader("Upload Exercise PDF", type="pdf", key="ex_up")
        submit    = st.form_submit_button("Confirm upload")

    if submit:
        errors = []
        if not topic:     errors.append("Topic is required.")
        if not summary:   errors.append("Summary is required.")
        if not lec_file:  errors.append("Lecture PDF is required.")
        if not ex_file:   errors.append("Exercise PDF is required.")
        if errors:
            for e in errors:
                st.error(e)
            return

        # upload both files
        folder_id = cfg["slides_lessons_folder_id"]
        lec_id    = upload_file_to_folder(folder_id, lec_file)
        ex_id     = upload_file_to_folder(folder_id, ex_file)
        lec_link  = f"https://drive.google.com/uc?export=download&id={lec_id}"
        ex_link   = f"https://drive.google.com/uc?export=download&id={ex_id}"

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
                ex_link,
            ]
        )
        st.success("✅ Lesson & exercise uploaded.")

def show_feedback(role, cfg):
    """(Unchanged) feedback form + display."""
    st.header("📋 Other Handouts & Feedback")
    if role.lower() == "tutor":
        with st.form("feedback_form"):
            fb      = st.file_uploader("Upload feedback slides (PDF)", type="pdf")
            note    = st.text_area("Comments for student")
            submit  = st.form_submit_button("Confirm upload")
        if submit:
            if not fb or not note:
                st.error("Both PDF and comment are required.")
            else:
                folder = cfg["slides_nonlesson_folder_id"]
                fid    = upload_file_to_folder(folder, fb)
                link   = f"https://drive.google.com/uc?export=download&id={fid}"
                append_record(
                    cfg["gsheet_id"],
                    "feedback",
                    [datetime.now().strftime("%Y-%m-%d"), fb.name, link, note]
                )
                st.success("✅ Feedback uploaded.")

    df_fb = fetch_records(cfg["gsheet_id"], "feedback")
    for _, r in df_fb.iterrows():
        st.info(
            f"**{r['file_name']}**  \n"
            f"[Download]({r['link']})  \n"
            f"> {r['comment']}"
        )


def render_handouts(role, cfg):
    """Top‐level tab layout for docs & lessons."""
    tabs = ["📚 Lessons & Resources", "📋 Other Handouts"]
    if role == "Tutor":
        tabs.append("✏️ Upload Lesson & Exercise")

    ui_tabs = st.tabs(tabs)

    with ui_tabs[0]:
        display_lessons(role, cfg)
    with ui_tabs[1]:
        show_feedback(role, cfg)
    if role == "Tutor":
        with ui_tabs[2]:
            # same lessons form appears here for clarity
            upload_lessons(role, cfg)

    
    