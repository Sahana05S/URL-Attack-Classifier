import streamlit as st
from pathlib import Path
import pandas as pd

from core.pipeline import analyze_urls

st.set_page_config(page_title="Successful Attacks", layout="wide")

BASE_CSS = Path("assets/style.css")
if BASE_CSS.exists():
    st.markdown(f"<style>{BASE_CSS.read_text()}</style>", unsafe_allow_html=True)

st.markdown("## 🚨 Successful Attacks")

# Prefer existing analysis rows; otherwise re-run on uploaded URLs; otherwise fallback to mock
analysis_rows = st.session_state.get("analysis_rows")
uploaded_urls = st.session_state.get("uploaded_urls")

results = analysis_rows
if not results and uploaded_urls:
    try:
        results = analyze_urls(uploaded_urls)
    except Exception as exc:
        st.error(f"Failed to analyze URLs: {exc}")
        st.stop()

if not results:
    # Light mock to avoid empty page when nothing uploaded
    mock_urls = [
        "http://example.local/login.php?id=1' OR 1=1",
        "http://evil.tk/admin/panel?cmd=cat%20/etc/passwd",
    ]
    results = analyze_urls(mock_urls)

# Filter for high risk only
high_risk = [r for r in results if str(r.get("risk_level", "")).lower() == "high"]

if not high_risk:
    st.info("No successful attacks detected.")
    st.stop()

for idx, row in enumerate(high_risk, start=1):
    url = row.get("url", "")
    risk_score = int(row.get("risk_score", 0))
    ml_prob = float(row.get("ml_probability", 0.0))
    ml_conf_pct = int(round(ml_prob * 100))
    rules = row.get("rules_triggered") or []
    rules_display = ", ".join(rules) if rules else "None"

    st.markdown(
        f"**{url}**\n\n"
        f"- Risk Score: {risk_score}\n"
        f"- ML confidence: {ml_conf_pct}%\n"
        f"- Rules: {rules_display}\n"
    )
    with st.expander("Why was this flagged?"):
        st.write(row.get("why_summary", "No explanation available"))
    st.markdown("---")
