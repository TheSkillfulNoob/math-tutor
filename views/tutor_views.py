import streamlit as st
from modules.docs_display import upload_lessons, display_lessons, show_feedback
from modules.paper_system import _add_p1_score, _add_p2_score

def tab_enter_scores(role, cfg, *_):
    """✍️ Enter Mock Scores (tutor only)"""
    if role.lower() == "tutor":
        st.header("✍️ Enter Mock Scores")
        _add_p1_score(cfg)
        _add_p2_score(cfg)

def tab_upload_lessons(role, cfg, *_):
    """📂 Upload Lesson & Exercise (tutor only)"""
    if role.lower() == "tutor":
        st.header("📂 Upload Lesson & Exercise")
        upload_lessons(role, cfg)
        st.markdown("---")
        st.subheader("📚 Current Lessons")
        display_lessons(cfg)
        st.markdown("---")

TUTOR_TABS = [
    ("✍️ Enter Scores", tab_enter_scores),
    ("📂 Upload Lessons", tab_upload_lessons),
]