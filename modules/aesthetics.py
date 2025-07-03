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


def render_progress(
    topics_df: pd.DataFrame,
    scores_p1: pd.DataFrame,
    scores_p2: pd.DataFrame
):
    st.header("Progress Tracker")    
    # ── Latest Results & Comments ──
    st.markdown("---")
    st.header("📋 Latest Paper Results & Feedback")
    
    # Paper 1
    # — Paper 1 section %
    s1 = scores_p1.copy()
    s1["Date"] = pd.to_datetime(s1["Date"])
    s1 = s1.sort_values("Date")
    # compute section‐% on the fly
    s1["A1_pct"] = s1["A1_raw"] / s1["A1_max"] * 100
    s1["A2_pct"] = s1["A2_raw"] / s1["A2_max"] * 100
    s1["B_pct"]  = s1["B_raw"]  / s1["B_max"]  * 100
    
    # — Paper 2 section %
    s2 = scores_p2.copy()
    s2["Date"] = pd.to_datetime(s2["Date"])
    s2 = s2.sort_values("Date")
    s2["A_pct"] = s2["A_raw"] / s2["A_max"] * 100
    s2["B_pct"] = s2["B_raw"] / s2["B_max"] * 100
    

    # Paper 1 latest
    latest_p1 = s1.iloc[-1]  # since s1 is sorted by Date
    frac1 = int(latest_p1["A1_raw"] + latest_p1["A2_raw"] + latest_p1["B_raw"])
    max1  = int(latest_p1["A1_max"] + latest_p1["A2_max"] + latest_p1["B_max"])
    pct1  = latest_p1["Total_pct"]

    st.subheader("Paper 1")
    c1, c2 = st.columns([0.35, 0.65])
    with c1:
        st.markdown(f"**Score:** {frac1}/{max1} ({pct1:.1f}%) \n**By Section**:\n[A1] {latest_p1["A1_raw"]}/{latest_p1["A1_max"]}; \t[A2] {latest_p1["A2_raw"]}/{latest_p1["A2_max"]}; \t[B] {latest_p1["B_raw"]}/{latest_p1["B_max"]}")
    with c2:
        st.markdown("**Comment:**") 
        st.write(latest_p1["Comments"] or "_No comment_")

    # Paper 2 latest
    latest_p2 = s2.iloc[-1]
    frac2 = int(latest_p2["A_raw"] + latest_p2["B_raw"])
    max2  = int(latest_p2["A_max"] + latest_p2["B_max"])
    pct2  = latest_p2["Total_pct"]

    st.subheader("Paper 2")
    c3, c4 = st.columns([0.35, 0.65])
    with c3:
        st.markdown(f"**Score:** {frac2}/{max2} ({pct2:.1f}%) \n**By Section\n**:\n[A] {latest_p2["A_raw"]}/{latest_p2["A_max"]}; \t[B] {latest_p2["B_raw"]}/{latest_p2["B_max"]}")
    with c4:
        st.markdown("**Comment:**") 
        st.write(latest_p2["Comments"] or "_No comment_")
    
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

    # Prepare each scores DF
    for df in (scores_p1, scores_p2):
        df["Date"] = pd.to_datetime(df["Date"])
        df.sort_values("Date", inplace=True)

    # Melt for section‐by‐section plotting
    s1_secs = scores_p1.melt(
        id_vars=["Date"],
        value_vars=["A1_pct","A2_pct","B_pct"],
        var_name="Section",
        value_name="Pct"
    )
    s1_tot  = scores_p1.assign(
        Total_pct=lambda d: d[["A1_raw","A2_raw","B_raw"]].sum(1)
                           / d[["A1_max","A2_max","B_max"]].sum(1)
                           * 100
    ).assign(
        MA5=lambda d: d["Total_pct"].rolling(5,1).mean()
    ).melt(
        id_vars=["Date"],
        value_vars=["Total_pct","MA5"],
        var_name="Metric",
        value_name="Pct"
    )

    s2_secs = scores_p2.melt(
        id_vars=["Date"],
        value_vars=["A_pct","B_pct"],
        var_name="Section",
        value_name="Pct"
    )
    s2_tot  = scores_p2.assign(
        Total_pct=lambda d: (d["A_raw"]+d["B_raw"])
                           / (d["A_max"]+d["B_max"])
                           * 100
    ).assign(
        MA5=lambda d: d["Total_pct"].rolling(5,1).mean()
    ).melt(
        id_vars=["Date"],
        value_vars=["Total_pct","MA5"],
        var_name="Metric",
        value_name="Pct"
    )

    # Build a helper to make an Altair chart
    def make_chart(df_long, color_field, title):
        return (
            alt.Chart(df_long)
               .mark_line(point=True, size=3)   # point=True draws dots
               .encode(
                   x=alt.X("Date:T", title=None),
                   y=alt.Y("Pct:Q",
                           scale=alt.Scale(domain=[0,100]),
                           title="Percent"),
                   **{color_field:alt.Color(f"{color_field}:N")}
               )
               .properties(height=250, width="container")
               .interactive()  # allow tooltip/zoom if you like
        )

    # Render side by side
    col1, col2 = st.columns(2)

    # Paper 1
    with col1:
        st.subheader("📑 Paper 1")
        st.markdown("**Section % Over Time**")
        st.altair_chart(make_chart(s1_secs, "Section", "Paper 1 Sections"), use_container_width=True)

        st.markdown("**Total % & 5-Exam MA**")
        st.altair_chart(make_chart(s1_tot, "Metric", "Paper 1 Total"), use_container_width=True)

    # Paper 2
    with col2:
        st.subheader("📑 Paper 2")
        st.markdown("**Section % Over Time**")
        st.altair_chart(make_chart(s2_secs, "Section", "Paper 2 Sections"), use_container_width=True)

        st.markdown("**Total % & 5-Exam MA**")
        st.altair_chart(make_chart(s2_tot, "Metric", "Paper 2 Total"), use_container_width=True)