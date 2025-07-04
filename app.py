from setup import configure_page, authenticate
import streamlit as st
from google_utils    import fetch_records
from modules         import aesthetics
from views.tutee_views   import tab_mock_papers, tab_latest_results
from views.common_views  import tab_topic_mastery, tab_lessons_and_handouts
from views.tutor_views   import tab_enter_scores, tab_upload_handouts

configure_page()
role = authenticate()
cfg  = st.secrets["math_tutor"]
sheet = cfg["gsheet_id"]

# fetch all sheets up front
df_topics   = fetch_records(sheet,"topics-breakdown")
df_quotes   = fetch_records(sheet,"quotes")
df_s1       = fetch_records(sheet,"scores_p1")
df_s2       = fetch_records(sheet,"scores_p2")
df_lessons  = fetch_records(sheet,"lessons")
df_feedback = fetch_records(sheet,"feedback")

# top-of-page box
aesthetics.show_weekly_quote(df_quotes, df_topics)

# now the three large tabs
tabs = st.tabs(["✍️ Mock Papers","💯 Progress","⚙️ Teacher"])

# Tab 1: Tutee only
with tabs[0]:
    tab_mock_papers(role, cfg)
    tab_latest_results(df_s1, df_s2)

# Tab 2: everybody
with tabs[1]:
    tab_topic_mastery(df_topics)
    tab_lessons_and_handouts(role, cfg)

# Tab 3: tutor-only
with tabs[2]:
    tab_enter_scores(role, cfg)
    tab_upload_handouts(role, cfg)
