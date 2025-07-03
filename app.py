from setup import configure_page, authenticate
import streamlit as st
from modules import paper_system, aesthetics, docs_display
from google_utils import fetch_records

cfg     = st.secrets["math_tutor"]
sheet   = "Math-tutor"

configure_page()
role = authenticate()

# pull each worksheet into a DataFrame
df_topics   = fetch_records(sheet, "topics-breakdown")
df_quotes   = fetch_records(sheet, "quotes")
df_scores1  = fetch_records(sheet, "scores_p1")
df_scores2  = fetch_records(sheet, "scores_p2")
df_lessons  = fetch_records(sheet, "lessons")
df_feedback = fetch_records(sheet, "feedback")

# Quote + weakest + countdown
aesthetics.show_weekly_quote(df_quotes, df_topics)

tab1, tab2, tab3 = st.tabs(["✍️ Mock Papers","💯 Progress","📄 Docs"])
with tab1:
    paper_system.render(role, cfg)
with tab2:
    aesthetics.render_progress(
        df_topics,
        df_scores1,
        df_scores2,
        df_lessons,
        df_feedback
    )
with tab3:
    docs_display.render(role, cfg)