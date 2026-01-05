import streamlit as st
from core.ui_shell import apply_global_styles, top_navbar
from core.pipeline import analyze_urls

st.set_page_config(page_title="Successful Attacks", layout="wide", initial_sidebar_state="collapsed")

apply_global_styles()
top_navbar("Dashboard")

# Auth guard
if not st.session_state.get("auth_ok"):
    st.session_state["post_login_target"] = "pages/4_Successful_Attacks.py"
    st.session_state.show_auth = True
    st.switch_page("app.py")

st.markdown(
    """
    <div class="glass-card stack">
      <div class="card-title">Successful Attacks</div>
      <div class="muted">High-risk URLs that cleared detection thresholds.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

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
    mock_urls = [
        "http://example.local/login.php?id=1' OR 1=1",
        "http://evil.tk/admin/panel?cmd=cat%20/etc/passwd",
    ]
    results = analyze_urls(mock_urls)

high_risk = [r for r in results if str(r.get("risk_level", "")).lower() == "high"]

if not high_risk:
    st.markdown(
        """
        <div class="glass-card stack">
          <div class="card-title">No successful attacks detected</div>
          <div class="muted">Upload fresh data or adjust detection settings to see results here.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

for row in high_risk:
    url = row.get("url", "")
    risk_score = int(row.get("risk_score", 0))
    ml_prob = float(row.get("ml_probability", 0.0))
    ml_conf_pct = int(round(ml_prob * 100))
    rules = row.get("rules_triggered") or []
    rules_display = ", ".join(rules) if rules else "None"

    st.markdown(
        f"""
        <div class="glass-card stack">
          <div class="card-title">🚨 {url}</div>
          <div class="muted">Risk Score: {risk_score}</div>
          <div class="muted">ML confidence: {ml_conf_pct}%</div>
          <div class="muted">Rules: {rules_display}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.expander("Why was this flagged?"):
        st.markdown(f"""<div class="glass-card">{row.get("why_summary", "No explanation available")}</div>""", unsafe_allow_html=True)
