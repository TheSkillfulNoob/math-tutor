import streamlit as st
import pandas as pd
import random
from datetime import date

# motivational quotes stored in a CSV
QUOTES_FILE = "data/quotes.csv"
SCORES_FILE = "data/scores.csv"
TOPICS_FILE = "data/topics-breakdown.csv"

def display_box(content, theme: str = "blue"):
    # define bg/text pairs for each theme
    styles = {
        "blue":  {"bg": "#0066cc", "fg": "#CCE5FF"},
        "red":   {"bg": "#cc0000", "fg": "#FFCCCC"},
        "green": {"bg": "#28a745", "fg": "#D4EDDA"},
    }
    # fallback to blue if unknown
    s = styles.get(theme, styles["blue"])

    st.markdown(
        f'''
        <div style="
            background-color: {s["bg"]};
            color: {s["fg"]};
            font-size: 20px;
            border-radius: 8px;
            padding: 0.5em 1em;
            margin-bottom: 0.5em;
        ">
            {content}
        </div>
        ''',
        unsafe_allow_html=True
    )

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



def show_weekly_quote(quotes_df: pd.DataFrame, topics_df: pd.DataFrame):
    week = pd.Timestamp.today().isocalendar().week
    q = quotes_df.iloc[week % len(quotes_df)]
    author = q.get("author", "")
    quote = q.get("quote", "")
    quote_text = f"“{quote}”\n\n— {author}"

    # 2) load & compute weakest sub-items each week —
    weakest = topics_df.nsmallest(3, "rate")

    # 4) Format into your info box
    weak_lines = [
        f"- {r['topic']}({r['index']}): Level {r['rate']}/7"
        for _, r in weakest.iterrows()
    ]
    weakest_text = "\n".join(weak_lines)
    
    # 3) Compute countdowns
    today = date.today()
    exam_dates = {
        "First Compulsory (9 Apr '26)": date(2026, 4, 9),
        "Math Exam (13 Apr '26)":    date(2026, 4, 13),
        "Last Subject (Bio, 20 Apr '26)": date(2026, 4, 20),
    }
    lines = []
    for label, dt in exam_dates.items():
        days = (dt - today).days
        if days >= 0:
            lines.append(f"**{label}**: {days} days")
        else:
            lines.append(f"**{label}**: 🏁 done")

    countdown_upcoming = "📅 Important Countdowns"

    # 3) Render in two columns
    col1, col2, col3 = st.columns([0.3, 0.35, 0.35])
    with col1:
        display_box(f"💡 Week {week} Quote", theme="blue")
        st.info(quote_text)
    with col2:
        display_box(f"🔴 Weakest sub-items", theme="red")
        st.info(weakest_text)
    with col3:
        display_box(countdown_upcoming, theme="green")
        st.markdown(f":red-background[• {lines[0]}]")
        st.markdown(f":green-background[• {lines[1]}]")
        st.markdown(f":rainbow-background[• {lines[2]}]")


def render_progress(
    topics_df: pd.DataFrame,
    scores_p1: pd.DataFrame,
    scores_p2: pd.DataFrame
):
    st.header("Progress Tracker")

    # ── 1) Topic-mastery chart (unchanged) ──
    df = topics_df.copy()
    df["core_topic"] = df["index"].map(TOPIC_MAP)
    df["strand"]     = df["index"].map(STRAND_MAP)
    avg = df.groupby(
        ["index","core_topic","strand"], as_index=False
    ).rate.mean()
    order = [TOPIC_MAP[i] for i in sorted(TOPIC_MAP)]
    topic_chart = (
        alt.Chart(avg)
           .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
           .encode(
             x=alt.X("core_topic:N", sort=order, axis=alt.Axis(labelAngle=-45)),
             y=alt.Y("rate:Q", title="Average Level (out of 7)"),
             color=alt.Color("strand:N",
               scale=alt.Scale(
                 domain=list(STRAND_COLORS.keys()),
                 range=list(STRAND_COLORS.values())
               ),
               legend=alt.Legend(title="Strand")
             )
           )
           .properties(height=350)
    )
    st.altair_chart(topic_chart, use_container_width=True)


    # ── 2) Paper 1 ──
    scores_p1 = scores_p1.copy()
    scores_p1["Date"] = pd.to_datetime(scores_p1["Date"])
    scores_p1 = scores_p1.sort_values("Date")

    st.subheader("Paper 1: Section Scores Over Time")
    st.line_chart(
        scores_p1.set_index("Date")[["A1","A2","B"]],
        use_container_width=True
    )

    st.subheader("Paper 1: Total Score + 5-Exam MA")
    scores_p1["MA5"] = scores_p1["Total"].rolling(5, min_periods=1).mean()
    st.line_chart(
        scores_p1.set_index("Date")[["Total","MA5"]],
        use_container_width=True
    )


    # ── 3) Paper 2 ──
    scores_p2 = scores_p2.copy()
    scores_p2["Date"] = pd.to_datetime(scores_p2["Date"])
    scores_p2 = scores_p2.sort_values("Date")

    st.subheader("Paper 2: Section Scores Over Time")
    st.line_chart(
        scores_p2.set_index("Date")[["A","B"]],
        use_container_width=True
    )

    st.subheader("Paper 2: Total Score + 5-Exam MA")
    scores_p2["MA5"] = scores_p2["Total"].rolling(5, min_periods=1).mean()
    st.line_chart(
        scores_p2.set_index("Date")[["Total","MA5"]],
        use_container_width=True
    )