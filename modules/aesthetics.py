import streamlit as st
import pandas as pd
import random

# motivational quotes stored in a CSV
QUOTES_FILE = "../data/quotes.csv"


def show_weekly_quote():
    df = pd.read_csv(QUOTES_FILE)
    # rotate quotes weekly (e.g. based on ISO week number)
    week = pd.Timestamp.today().isocalendar().week
    quote = df.iloc[week % len(df)]['quote']
    author = df.iloc[week % len(df)]['author']
    st.info(f"💡 {quote} - \n{author}")


def render_progress(config):
    st.header("Progress Tracker")
    # load levels from CSV
    levels = pd.read_csv(config['levels_csv'])
    st.subheader("Topic Mastery")
    for _, row in levels.iterrows():
        st.write(f"**{row['topic']}**")
        st.progress(int(row['mastery'] * 100))

    # paper scores (assumes a CSV)
    scores = pd.read_csv(config['scores_csv'])
    st.subheader("Section Scores")
    st.bar_chart(scores.set_index('section')['score'])