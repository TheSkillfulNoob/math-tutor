# views/tutee_views.py
import streamlit as st
from modules.paper_system import _show_available_papers
from modules.aesthetics   import show_latest_results

def tab_mock_papers(role, cfg):
    if role.lower()=="tutee":
        _show_available_papers(cfg)
    else:
        st.info("Mock-papers only for students.")

def tab_latest_results(scores_p1, scores_p2):
    show_latest_results(scores_p1, scores_p2)