import streamlit as st, plotly.express as px
from pathlib import Path
import pandas as pd
import io

BASE_CSS = Path("assets/style.css")
THEME_FILES = {
    "Dark": Path("assets/dark-theme.css"),
    "Light": Path("assets/light-theme.css"),
}


def apply_theme_from_session():
    theme = st.session_state.get("theme", "Dark")
    if BASE_CSS.exists():
        with BASE_CSS.open() as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    css_path = THEME_FILES.get(theme, THEME_FILES["Dark"])
    if css_path.exists():
        with css_path.open() as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


if "theme" not in st.session_state:
    st.session_state["theme"] = "Dark"

apply_theme_from_session()

# Top header (single columns layout)
header_cols = st.columns([2, 1, 1, 1, 1])
header_cols[0].markdown("**URL Attack Detection System**")
header_cols[1].page_link("pages/1_Home.py", label="Home")
header_cols[2].page_link("pages/2_Upload.py", label="Upload")
header_cols[3].page_link("pages/3_Dashboard.py", label="Dashboard")
with header_cols[4]:
    current_theme = st.session_state["theme"]
    toggle_val = st.toggle("Dark theme", value=current_theme == "Dark", key="theme_toggle_dashboard")
    new_theme = "Dark" if toggle_val else "Light"
    if new_theme != current_theme:
        st.session_state["theme"] = new_theme
        apply_theme_from_session()

rows = st.session_state.get("analysis_rows")
if not rows:
    st.warning("Upload logs first to view the dashboard.")
    st.stop()


def risk_icon(level: str) -> str:
    level = (level or "").lower()
    if level == "high":
        return "🔴"
    if level == "medium":
        return "🟠"
    return "🟢"


display_df = pd.DataFrame(rows)
display_df.rename(
    columns={
        "url": "URL",
        "ml_label": "ML Label",
        "ml_probability": "ML Probability",
        "rules_triggered": "Rules Triggered",
        "risk_score": "Risk Score",
        "risk_level": "Risk Level",
        "why_summary": "Why Summary",
    },
    inplace=True,
)

# Sort by highest risk first
if not display_df.empty and "Risk Score" in display_df.columns:
    display_df.sort_values(by="Risk Score", ascending=False, inplace=True)

# Sidebar filter for risk levels
selected_levels = st.sidebar.multiselect(
    "Risk levels", options=["High", "Medium", "Low"], default=["High", "Medium", "Low"]
)
filtered_df = (
    display_df[display_df["Risk Level"].str.title().isin(selected_levels)] if selected_levels else display_df.copy()
)

# 1. Title row
title_section = st.container()
with title_section:
    header_cols = st.columns([3, 1])
    header_cols[0].title("Dashboard")
    with header_cols[1]:
        if st.button("Successful Attacks", type="secondary", use_container_width=True):
            st.switch_page("pages/4_Successful_Attacks.py")

# 2. Metrics row
metrics_section = st.container()
with metrics_section:
    total_logs = len(filtered_df)
    attacks = sum(filtered_df["ML Label"] == "malicious") if not filtered_df.empty else 0
    high_risk = sum(filtered_df["Risk Level"].str.lower() == "high") if not filtered_df.empty else 0
    mcols = st.columns(3)
    mcols[0].metric("Total Logs", f"{total_logs:,}")
    mcols[1].metric("Detected Attacks", f"{attacks:,}")
    mcols[2].metric("High Risk", f"{high_risk:,}")

# Export current view
export_buf = io.StringIO()
filtered_df.to_csv(export_buf, index=False)
st.download_button(
    label="Export filtered results (CSV)",
    data=export_buf.getvalue(),
    file_name="analysis_results.csv",
    mime="text/csv",
)

# 3. Traffic list
table_section = st.container()
with table_section:
    st.markdown("### Traffic Overview")
    st.caption("All Traffic (analyzed via core.pipeline.analyze_urls)")

    if filtered_df.empty:
        st.info("No data to display for the selected filters.")
    else:
        for idx, row in filtered_df.iterrows():
            icon = risk_icon(row.get("Risk Level", "Low"))
            url_text = row.get("URL", "")
            risk_level = row.get("Risk Level", "Low")
            risk_score = int(row.get("Risk Score", 0))
            ml_prob = float(row.get("ML Probability", 0.0))
            ml_conf_pct = int(round(ml_prob * 100))
            rules_triggered = row.get("Rules Triggered") or []
            if isinstance(rules_triggered, str):
                rules_display = rules_triggered
            else:
                rules_display = ", ".join(rules_triggered) if rules_triggered else "None"

            risk_level_lower = str(risk_level).lower()
            if risk_level_lower == "high":
                st.error(f"High risk URL (score {risk_score})", icon="⚠️")
            elif risk_level_lower == "medium":
                st.info(f"Medium risk URL (score {risk_score})")

            st.markdown(
                f"{icon} **{url_text}**\n\n"
                f"- Risk: {risk_level} ({risk_score})\n"
                f"- ML confidence: {ml_conf_pct}%\n"
                f"- Rules: {rules_display}\n"
            )
            with st.expander("Why was this flagged?"):
                st.write(row.get("Why Summary", "No explanation available"))
            st.markdown("---")

# 4. Charts row
charts_section = st.container()
with charts_section:
    chart_cols = st.columns(2)
    with chart_cols[0]:
        st.markdown("#### Attack Distribution")
        if not filtered_df.empty:
            attack_fig = px.bar(filtered_df, x="ML Label")
            attack_fig.update_layout(
                transition={"duration": 700, "easing": "cubic-in-out"},
                margin=dict(l=10, r=10, t=30, b=10),
            )
            attack_fig.update_traces(base=0)
            st.plotly_chart(attack_fig, use_container_width=True)
        else:
            st.caption("No attacks detected.")

    with chart_cols[1]:
        st.markdown("#### Risk Mix")
        if not filtered_df.empty:
            risk_fig = px.pie(filtered_df, names="Risk Level")
            risk_fig.update_layout(transition={"duration": 700, "easing": "cubic-in-out"})
            risk_fig.update_traces(sort=False)
            st.plotly_chart(risk_fig, use_container_width=True)
        else:
            st.caption("No data to chart.")
