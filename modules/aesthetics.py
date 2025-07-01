import streamlit as st
import pandas as pd
import random
from datetime import date

# motivational quotes stored in a CSV
QUOTES_FILE = "data/quotes.csv"
SCORES_FILE = "data/scores.csv"
TOPICS_FILE = "data/topics-breakdown.csv"

def display_box(content):
    st.markdown(
        f'<p style="background-color:#0066cc;color:#CCE5FF;font-size:24px;border-radius:2%;">{content}</p>',
        unsafe_allow_html=True)

import altair as alt

# 14-topic names & strand grouping
TOPIC_MAP = {
    1: "Numbers & Divisibility",
    2: "Proportions",
    3: "Basic Algebra",
    4: "Geometry",
    5: "Trigonometry",
    6: "App. of Trig",
    7: "Mensuration",
    8: "Eqns in One Unknown",
    9: "Coordinate Geometry",
    10: "Functions & Graphs",
    11: "Inequalities",
    12: "Sequences",
    13: "Probability",
    14: "Statistics",
}

STRAND_MAP = {
    1: "Foundations",
    2: "Foundations",
    3: "Foundations",
    4: "Measures",
    5: "Measures",
    6: "Measures",
    7: "Measures",
    8: "Algebra & Graphs",
    9: "Algebra & Graphs",
    10: "Algebra & Graphs",
    11: "Algebra & Graphs",
    12: "Data Handling",
    13: "Data Handling",
    14: "Data Handling",
}

# pick four distinct hex-colours for your strands:
STRAND_COLORS = {
    "Foundations":   "#1f77b4",
    "Measures":      "#ff7f0e",
    "Algebra & Graphs": "#2ca02c",
    "Data Handling": "#d62728",
}

def render_progress():
    # 1) load & annotate
    df = pd.read_csv("data/topics-breakdown.csv")
    df["core_topic"] = df["chapter"].map(TOPIC_MAP)
    df["strand"]     = df["chapter"].map(STRAND_MAP)

    # 2) compute per-topic average
    avg = (
        df
        .groupby(["chapter","core_topic","strand"], as_index=False)
        .level
        .mean()
    )

    # 3) build an Altair bar chart with strand-colours
    order = [TOPIC_MAP[i] for i in sorted(TOPIC_MAP)]
    chart = (
        alt.Chart(avg)
           .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
           .encode(
               x=alt.X("core_topic:N",
                       sort=order,
                       title=None,
                       axis=alt.Axis(labelAngle=-45)),
               y=alt.Y("level:Q",
                       title="Average Level (out of 7)"),
               color=alt.Color("strand:N",
                               scale=alt.Scale(
                                   domain=list(STRAND_COLORS.keys()),
                                   range=list(STRAND_COLORS.values())
                               ),
                               legend=alt.Legend(title="Strand"))
           )
           .properties(height=400, width=800)
    )
    st.altair_chart(chart, use_container_width=True)

def show_weekly_quote():
    # 1) Load this week's quote
    df = pd.read_csv(QUOTES_FILE)
    today_ts = pd.Timestamp.today()
    week = today_ts.isocalendar().week
    row = df.iloc[week % len(df)]
    quote = row["quote"]
    author = row.get("author", "")
    quote_text = f"“{quote}”\n\n— {author}"

    # 2) load & compute weakest sub-items each week —
    BREAKDOWN_FILE = "data/topics-breakdown.csv"
    df_lv = pd.read_csv(BREAKDOWN_FILE)

    # 2) (Optional) if you haven’t already, map numeric index→topic name
    #    using the same TOPIC_MAP you used in your progress chart
    df_lv["core_topic"] = df_lv["index"].map(TOPIC_MAP)

    # 3) Find the 3 weakest sub‐items
    weakest = df_lv.nsmallest(3, "level")

    # 4) Format into your info box
    weak_lines = [
        f"- {r['sub_item']} ({r['core_topic']}): Level {r['level']}/7"
        for _, r in weakest.iterrows()
    ]
    weakest_text = "🔴 Three weakest sub-items\n\n" + "\n".join(weak_lines)
    
    # 3) Compute countdowns
    today = date.today()
    exam_dates = {
        "First Compulsory (9 Apr 2026)": date(2026, 4, 9),
        "Math Exam (13 Apr 2026)":    date(2026, 4, 13),
        "Last Subject (Econ, 4 May 2026)": date(2026, 5, 4),
    }
    lines = []
    for label, dt in exam_dates.items():
        days = (dt - today).days
        if days >= 0:
            lines.append(f"**{label}**: {days} days to go")
        else:
            lines.append(f"**{label}**: 🏁 done")

    countdown_upcoming = "📅 Important Countdowns"

    # 3) Render in two columns
    col1, col2, col3 = st.columns([0.45, 0.22, 0.33])
    with col1:
        display_box(f"💡 Week {week} Quote")
        st.info(quote_text)
    with col2:
        st.info(weakest_text)
    with col3:
        display_box(countdown_upcoming)
        st.markdown(f":red-background[• {lines[0]}]")
        st.markdown(f":green-background[• {lines[1]}]")
        st.markdown(f":rainbow-background[• {lines[2]}]")


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