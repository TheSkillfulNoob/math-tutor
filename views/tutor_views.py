# views/tutor_views.py
import streamlit as st
from modules.paper_system import _add_p1_score, _add_p2_score
from modules.docs_display  import show_lessons, show_feedback

def tab_enter_scores(role, cfg):
    if role.lower()=="tutor":
        st.subheader("✍️ Enter Mock Scores")
        _add_p1_score(cfg)
        _add_p2_score(cfg)

def tab_upload_handouts(role, cfg):
    if role.lower()=="tutor":
        st.subheader("📂 Upload Handouts")
        show_lessons(role, cfg)
        st.markdown("---")
        show_feedback(role, cfg)