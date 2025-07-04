import streamlit as st
from modules.aesthetics   import show_topic_mastery
from modules.docs_display import show_lessons, show_feedback

def tab_topic_mastery(role, cfg, topics_df, *_):
    """📊 Topic Mastery (everyone)"""
    st.header("📊 Topic Mastery")
    show_topic_mastery(topics_df)

def tab_lessons_and_handouts(role, cfg, _1, _2, lessons_df, feedback_df):
    """📚 Lessons & 📋 Non-Lesson Handouts (everyone)"""
    st.header("📚 Lessons & Summary")
    show_lessons(role, cfg)
    st.markdown("---")
    st.header("📋 Other Handouts")
    show_feedback(role, cfg)

COMMON_TABS = [
    ("📊 Topic Mastery",         tab_topic_mastery),
    ("📚 Lessons & Handouts",    tab_lessons_and_handouts),
]