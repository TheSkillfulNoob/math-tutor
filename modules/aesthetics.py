import streamlit as st
import pandas as pd
import random
from datetime import date

# motivational quotes stored in a CSV
QUOTES_FILE = "data/quotes.csv"

def display_box(content):
    st.markdown(
        f'<p style="background-color:#0066cc;color:#CCE5FF;font-size:24px;border-radius:2%;">{content}</p>',
        unsafe_allow_html=True)

def show_weekly_quote():
    # 1) Load this week's quote
    df = pd.read_csv(QUOTES_FILE)
    today_ts = pd.Timestamp.today()
    week = today_ts.isocalendar().week
    row = df.iloc[week % len(df)]
    quote = row["quote"]
    author = row.get("author", "")
    quote_text = f"“{quote}”\n\n— {author}"

    # 2) Compute countdowns
    today = date.today()
    exam_dates = {
        "First Compulsory (9 Apr 2026)": date(2026, 4, 9),
        "Math Exam (13 Apr 2026)":    date(2026, 4, 13),
        "Results Release (15 Jul 2026)": date(2026, 7, 15),
    }
    lines = []
    for label, dt in exam_dates.items():
        days = (dt - today).days
        if days >= 0:
            lines.append(f"**{label}**: {days} days to go")
        else:
            lines.append(f"**{label}**: 🏁 done")

    countdown_text = "📅 Upcoming\n\n" + "\n\n".join(lines)

    # 3) Render in two columns
    col1, col2 = st.columns([0.58, 0.42])
    with col1:
        display_box(f"💡 Week {week} Quote")
        st.info(quote_text)
    with col2:
        st.info(countdown_text)


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