from setup import configure_page, authenticate
import streamlit as st
from csv_utils import load_levels
from google_utils import fetch_records, push_dataframe
from modules import paper_system, aesthetics, docs_display

# Pull your entire config namespace directly:
cfg = st.secrets["math_tutor"]

configure_page()
authenticate()

# show weekly quote
aesthetics.show_weekly_quote()

tab1, tab2, tab3 = st.tabs(["Exercises", "Progress", "Docs"])
with tab1:
    paper_system.render(cfg, fetch_records, push_dataframe)
with tab2:
    levels = load_levels(cfg["levels_csv"])
    aesthetics.render_progress(levels)
with tab3:
    docs_display.render(cfg)