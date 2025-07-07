import streamlit as st
from modules.aesthetics   import show_topic_mastery
from modules.docs_display import display_lessons, show_feedback

def tab_topic_mastery(role, cfg, topics_df, *_):
    """📊 Topic Mastery (everyone)"""
    show_topic_mastery(topics_df)
    
def tab_lessons_and_handouts(role, cfg, *_):
    """📚 Lessons & Summary + 📋 Other Handouts (all users)"""
    st.header("📚 Lessons & Summary")
    display_lessons(cfg)
    st.markdown("---")
    show_feedback(role, cfg)

COMMON_TABS = [
    ("📚 Lessons & Handouts", tab_lessons_and_handouts),
    # I missed this line smh
    ("📊 Topic Mastery", tab_topic_mastery), 
]
