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


def show_latest_results(scores_p1: pd.DataFrame, scores_p2: pd.DataFrame):
    """Tab 1: Latest paper fractions + comments."""
    st.header("📋 Latest Paper Results & Feedback")

    # assume your s1 and s2 already have the raw/max columns and Total_pct
    s1 = scores_p1.copy().sort_values("Date")
    s2 = scores_p2.copy().sort_values("Date")

    for label, df in [("Paper 1", s1), ("Paper 2", s2)]:
        latest = df.iloc[-1]
        # compute raw & max
        if label == "Paper 1":
            obt = latest["A1_raw"] + latest["A2_raw"] + latest["B_raw"]
            mx  = latest["A1_max"] + latest["A2_max"] + latest["B_max"]
        else:
            obt = latest["A_raw"] + latest["B_raw"]
            mx  = latest["A_max"] + latest["B_max"]
        pct = latest["Total_pct"]
        
        c1, c2 = st.columns([0.35, 0.65])
        with c1:
            st.subheader(f"{label} - Set {latest["Set"].split("-")[0]}")
            st.markdown(f"**Score:** {obt}/{mx} ({pct:.1f}%)")
            if label == "Paper 1":
                st.markdown(f"**[A1]** {latest["A1_raw"]}/{latest["A1_max"]}; **[A2]** {latest["A2_raw"]}/{latest["A2_max"]}; **[B]** {latest["B_raw"]}/{latest["B_max"]}")
            else:
                st.markdown(f"**[A]** {latest["A_raw"]}/{latest["A_max"]}; **[B]** {latest["B_raw"]}/{latest["B_max"]}")
        with c2:
            st.info(f"**Comment:**\n\n{latest.get("Comments", "_No comment_")}")
    st.markdown("---")

def show_topic_mastery(topics_df: pd.DataFrame):
    """Tab 2: Bar chart of the 14 core topics, then an expandable list of subtopics."""
    st.header("📊 Topic Mastery")

    # 1) Prepare the averaged bar‐chart data
    df = topics_df.copy()
    df["core_topic"] = df["index"].map(TOPIC_MAP)
    df["strand"]     = df["index"].map(STRAND_MAP)

    avg = (
        df
        .groupby(["index","core_topic","strand"], as_index=False)
        .rate.mean()
    )
    order = [TOPIC_MAP[i] for i in sorted(TOPIC_MAP)]

    chart = (
        alt.Chart(avg)
           .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
           .encode(
             x=alt.X("core_topic:N",
                     sort=order,
                     axis=alt.Axis(labelAngle=-45)),
             y=alt.Y("rate:Q",
                     title="Average Level (out of 7)",
                     scale=alt.Scale(domain=[1,7])),
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
    st.altair_chart(chart, use_container_width=True)

    st.markdown("---")
    st.header("🗂 Chapters & Sub-topics by Strand")
    # Define which chapter‐indexes belong in each strand (1-3, 4-7, 8-11, 12-14)
    strand_order = ["Foundations", "Measures", "Algebra & Graphs", "Data Handling"]
    strand_chapters = {
        "Foundations":        [1, 2, 3],
        "Measures":           [4, 5, 6, 7],
        "Algebra & Graphs":   [8, 9, 10, 11],
        "Data Handling":      [12, 13, 14],
    }

    cols = st.columns(4)
    for col, strand in zip(cols, strand_order):
        with col:
            st.subheader(strand)
            color = STRAND_COLORS[strand]

            for idx in strand_chapters[strand]:
                chapter_name = TOPIC_MAP[idx]
                # Use an HTML‐styled label so the expander header is in the strand colour
                label = (
                    f"<span style='font-weight:bold;color:{color};'>"
                    f"{idx}. {chapter_name}"
                    "</span>"
                )
                with st.expander(label, expanded=False):
                    # pull all names (stored as topics) for this chapter
                    subs = topics_df.loc[
                        topics_df["index"] == idx, "topic"].tolist()
                    for sub in subs:
                        bullet = f"<span style='color:{color}'>&#9679;"
                        st.markdown(f"{bullet} {sub}: {topics_df.loc[topics_df["index"] == idx, "rate"]}/ 7 </span>", unsafe_allow_html=True)

    st.markdown("---")

def show_lessons_summary(lessons_df: pd.DataFrame, feedback_df: pd.DataFrame):
    """Tab 3: two-column lessons & summary."""
    st.header("📝 Lessons & Key Points / Summary")
    for _, r in lessons_df.sort_values("Date", ascending=False).iterrows():
        col1, col2 = st.columns([0.4, 0.6])
        with col1:
            st.subheader(f"{r['Date']}")
            st.markdown(f"**{r['Topic']}**")
            st.write(r["Summary"])
        with col2:
            st.subheader("Resources/ Reminders")
            st.markdown("TODO implement: Slides and Exercises")
            st.write(r["Feedback"])
        st.markdown("---")

def render_progress(
    topics_df: pd.DataFrame,
    scores_p1: pd.DataFrame,
    scores_p2: pd.DataFrame,
    lessons_df: pd.DataFrame,
    summary_df: pd.DataFrame
):
    tabs = st.tabs([
        "📋 Latest Results",
        "📊 Topic Mastery",
        "📝 Lessons & Summary"
    ])
    with tabs[0]:
        show_latest_results(scores_p1, scores_p2)
    with tabs[1]:
        show_topic_mastery(topics_df)
    with tabs[2]:
        show_lessons_summary(lessons_df, summary_df)