# app.py
import streamlit as st
from setup import configure_page, authenticate
from google_utils import fetch_records
import streamlit as st

from views.tutee_views   import TUTEE_TABS
from views.common_views  import COMMON_TABS
from views.tutor_views   import TUTOR_TABS
from modules import aesthetics

configure_page()
role = authenticate()
cfg  = st.secrets["math_tutor"]
sheet = cfg["gsheet_id"]

# Fetch everything you need
df_topics   = fetch_records(sheet, "topics-breakdown")
df_quotes   = fetch_records(sheet, "quotes")
df_s1       = fetch_records(sheet, "scores_p1")
df_s2       = fetch_records(sheet, "scores_p2")
df_lessons  = fetch_records(sheet, "lessons")
df_feedback = fetch_records(sheet, "feedback")

# Top‐of‐page aesthetic box
aesthetics.show_weekly_quote(df_quotes, df_topics)

# Build a single ordered list of tabs depending on role
tabs_to_show = []
if role.lower() == "tutee":
    tabs_to_show += TUTEE_TABS
tabs_to_show += COMMON_TABS
if role.lower() == "tutor":
    tabs_to_show += TUTOR_TABS

# Create the Streamlit tabs
labels = [label for label, _ in tabs_to_show]
sts    = st.tabs(labels)

# Call each render function with the arguments it needs
for (label, fn), tab in zip(tabs_to_show, sts):
    with tab:
        # fn signature is (role,cfg,df_topics,df_s1,df_s2,df_lessons,df_feedback)
        fn(role, cfg, df_topics, df_s1, df_s2, df_lessons, df_feedback)
