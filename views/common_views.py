# views/common_views.py
import streamlit as st
from modules.aesthetics import show_topic_mastery
from modules.docs_display import show_lessons, show_feedback

def tab_topic_mastery(topics_df):
    show_topic_mastery(topics_df)

def tab_lessons_and_handouts(role, cfg):
    show_lessons(role, cfg)    # guarded internally by role
    st.markdown("---")
    show_feedback(role, cfg)   # guarded internally by role
