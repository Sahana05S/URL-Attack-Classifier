import streamlit as st
import pandas as pd
from core.pipeline import analyze_urls
from core.ui_shell import apply_global_styles, top_navbar

st.set_page_config(page_title="Upload", layout="wide", initial_sidebar_state="collapsed")

apply_global_styles()
top_navbar("Upload")

# Auth guard
if not st.session_state.get("auth_ok"):
    st.session_state["post_login_target"] = "pages/2_Upload.py"
    st.warning("Please login to continue.")
    st.session_state.show_auth = True
    st.switch_page("app.py")

st.session_state.setdefault("upload_redirect", False)
st.session_state.setdefault("analysis_rows", None)
st.session_state.setdefault("uploaded_urls", None)

st.markdown(
    """
    <div class="glass-card stack">
      <div class="card-title">Upload URL Access Logs</div>
      <div class="muted">
        Upload a CSV containing columns like <strong>url</strong>, <strong>status_code</strong>, <strong>source_ip</strong>, <strong>user_agent</strong>,
        and optional labels/verdicts. Data stays local; once processed you'll be redirected to the dashboard.
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

file = st.file_uploader("CSV file", type="csv", label_visibility="collapsed")

if file:
    try:
        df = pd.read_csv(file)
        if "url" not in df.columns:
            st.error("Uploaded CSV must contain a 'url' column.")
        else:
            urls = df["url"].dropna().astype(str).tolist()
            analysis_rows = analyze_urls(urls)
            st.session_state["uploaded_urls"] = urls
            st.session_state["analysis_rows"] = analysis_rows
            st.session_state["upload_redirect"] = True
            st.success("Logs uploaded successfully. Redirecting to dashboard...")
            st.balloons()
    except Exception as exc:
        st.error(f"Failed to process file: {exc}")

if st.session_state.get("upload_redirect"):
    st.switch_page("pages/3_Dashboard.py")
