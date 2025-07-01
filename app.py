from setup import configure_page, authenticate
import streamlit as st
import yaml
from csv_utils import load_levels, save_csv_buffer
from google_utils import fetch_records, push_dataframe
from modules import paper_system, aesthetics, docs_display

# Load config
with open("config.yaml") as f:
    cfg = yaml.safe_load(f)

configure_page()
authenticate()

# show weekly quote
aesthetics.show_weekly_quote("data/quotes.csv")

tab1, tab2, tab3 = st.tabs(["Exercises", "Progress", "Docs"])
with tab1:
    paper_system.render(cfg, fetch_records, push_dataframe)
with tab2:
    levels = load_levels("data/levels.csv")
    aesthetics.render_progress(levels)
with tab3:
    docs_display.render(cfg)