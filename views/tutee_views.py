import streamlit as st
from modules.paper_system import _show_available_papers
from modules.aesthetics   import show_latest_results

def tab_mock_papers(role, cfg, *_):
    """✍️ Mock Papers (tutee only)"""
    if role.lower() == "tutee":
        _show_available_papers(cfg)
    else:
        st.info("Mock-papers only for students.")

def tab_latest_results(role, cfg,
                       _topics_df,    # catch the topics param
                       scores_p1,
                       scores_p2,
                       *_):
    """📋 Latest Results (tutee only)"""
    if role.lower() == "tutee":
        show_latest_results(scores_p1, scores_p2)

TUTEE_TABS = [
    ("✍️ Mock Papers",    tab_mock_papers),
    ("📈 Latest Results", tab_latest_results),
]