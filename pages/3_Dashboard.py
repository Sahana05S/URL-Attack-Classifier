import io
import pandas as pd
import plotly.express as px
import streamlit as st
from core.ui_shell import apply_global_styles, top_navbar

PLOTLY_TEMPLATE = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(6,30,41,0.75)",
    "font": {"color": "#F3F4F4"},
    "colorway": ["#5F9598", "#1D546D", "#F3F4F4"],
}
GRID_STYLE = {"xaxis": {"gridcolor": "rgba(243,244,244,0.12)"}, "yaxis": {"gridcolor": "rgba(243,244,244,0.12)"}}

st.set_page_config(page_title="Dashboard", layout="wide", initial_sidebar_state="collapsed")

apply_global_styles()
top_navbar("Dashboard")

# Auth guard
if not st.session_state.get("auth_ok"):
    st.session_state["post_login_target"] = "pages/3_Dashboard.py"
    st.session_state.show_auth = True
    st.switch_page("app.py")

rows = st.session_state.get("analysis_rows")
if not rows:
    st.markdown(
        """
        <div class="glass-card stack">
          <div class="card-title">No data yet</div>
          <div class="muted">Upload logs from the Upload page to populate this dashboard.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()


def risk_icon(level: str) -> str:
    level = (level or "").lower()
    if level == "high":
        return "🚨"
    if level == "medium":
        return "⚠️"
    return "✅"


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

st.markdown(
    """
    <div class="glass-card stack">
      <div class="card-title">Dashboard</div>
      <div class="muted">Analyze recent URL scans, risk levels, and detection reasons.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Filters within the main page
selected_levels = st.multiselect(
    "Risk levels",
    options=["High", "Medium", "Low"],
    default=["High", "Medium", "Low"],
    label_visibility="collapsed",
)
filtered_df = (
    display_df[display_df["Risk Level"].str.title().isin(selected_levels)] if selected_levels else display_df.copy()
)

export_buf = io.StringIO()
filtered_df.to_csv(export_buf, index=False)

st.markdown(
    """
    <div class="glass-card stack">
      <div class="card-title">Controls</div>
      <div class="muted">Export the current view or jump to successful attack details.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

control_cols = st.columns(2)
with control_cols[0]:
    st.download_button(
        label="Export filtered results (CSV)",
        data=export_buf.getvalue(),
        file_name="analysis_results.csv",
        mime="text/csv",
        use_container_width=True,
    )
with control_cols[1]:
    if st.button("Successful Attacks", type="secondary", use_container_width=True):
        st.switch_page("pages/4_Successful_Attacks.py")

# 1. Metrics row
total_logs = len(filtered_df)
attacks = sum(filtered_df["ML Label"] == "malicious") if not filtered_df.empty else 0
high_risk = sum(filtered_df["Risk Level"].str.lower() == "high") if not filtered_df.empty else 0

metrics_html = f"""
<div class="card-grid">
  <div class="glass-card">
    <div class="label muted">Total Logs</div>
    <div class="value">{total_logs:,}</div>
  </div>
  <div class="glass-card">
    <div class="label muted">Detected Attacks</div>
    <div class="value">{attacks:,}</div>
  </div>
  <div class="glass-card">
    <div class="label muted">High Risk</div>
    <div class="value">{high_risk:,}</div>
  </div>
</div>
"""
st.markdown(metrics_html, unsafe_allow_html=True)

# 2. Traffic list
st.markdown(
    """
    <div class="glass-card stack">
      <div class="card-title">Traffic Overview</div>
      <div class="muted">All traffic analyzed via core.pipeline.analyze_urls</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if filtered_df.empty:
    st.markdown(
        """
        <div class="glass-card stack">
          <div class="card-title">No data to display</div>
          <div class="muted">Adjust the risk filters or upload more logs.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    for _, row in filtered_df.iterrows():
        icon = risk_icon(row.get("Risk Level", "Low"))
        url_text = row.get("URL", "")
        risk_level = row.get("Risk Level", "Low")
        risk_score = int(row.get("Risk Score", 0))
        ml_prob = float(row.get("ML Probability", 0.0))
        ml_conf_pct = int(round(ml_prob * 100))
        rules_triggered = row.get("Rules Triggered") or []
        rules_display = (
            rules_triggered
            if isinstance(rules_triggered, str)
            else ", ".join(rules_triggered) if rules_triggered else "None"
        )

        st.markdown(
            f"""
            <div class="glass-card stack">
              <div class="card-title">{icon} {url_text}</div>
              <div class="muted">Risk: {risk_level} ({risk_score}) • ML confidence: {ml_conf_pct}%</div>
              <div class="muted">Rules: {rules_display}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.expander("Why was this flagged?"):
            why = row.get("Why Summary", "No explanation available")
            st.markdown(f"""<div class="glass-card">{why}</div>""", unsafe_allow_html=True)

# 3. Charts row
chart_cols = st.columns(2)
with chart_cols[0]:
    st.markdown(
        """
        <div class="glass-card stack">
          <div class="card-title">Attack Distribution</div>
          <div class="muted">Count of benign vs malicious URLs</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if not filtered_df.empty:
        attack_fig = px.bar(filtered_df, x="ML Label")
        attack_fig.update_layout(
            transition={"duration": 700, "easing": "cubic-in-out"},
            margin=dict(l=10, r=10, t=30, b=10),
            **PLOTLY_TEMPLATE,
            **GRID_STYLE,
        )
        attack_fig.update_traces(base=0)
        st.plotly_chart(attack_fig, use_container_width=True)
    else:
        st.caption("No attacks detected.")

with chart_cols[1]:
    st.markdown(
        """
        <div class="glass-card stack">
          <div class="card-title">Risk Mix</div>
          <div class="muted">Distribution of risk levels</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if not filtered_df.empty:
        risk_fig = px.pie(filtered_df, names="Risk Level")
        risk_fig.update_layout(
            transition={"duration": 700, "easing": "cubic-in-out"},
            margin=dict(l=10, r=10, t=30, b=10),
            **PLOTLY_TEMPLATE,
            **GRID_STYLE,
        )
        risk_fig.update_traces(sort=False, pull=[0.02] * len(risk_fig.data))
        st.plotly_chart(risk_fig, use_container_width=True)
    else:
        st.caption("No data to chart.")
