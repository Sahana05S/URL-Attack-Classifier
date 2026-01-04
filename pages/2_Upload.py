import streamlit as st
from pathlib import Path
import pandas as pd
from core.pipeline import analyze_urls

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
    toggle_val = st.toggle("Dark theme", value=current_theme == "Dark", key="theme_toggle_upload")
    new_theme = "Dark" if toggle_val else "Light"
    if new_theme != current_theme:
        st.session_state["theme"] = new_theme
        apply_theme_from_session()

st.title("Upload Logs")
st.session_state.setdefault("upload_redirect", False)
st.session_state.setdefault("analysis_rows", None)
st.session_state.setdefault("uploaded_urls", None)

with st.container():
    st.markdown(
        """
        <div style="max-width: 900px; margin: 0 auto; background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 18px 20px; box-shadow: var(--shadow);">
            <div style="font-weight: 800; font-size: 1.15rem; margin-bottom: 6px;">Upload URL Access Logs</div>
            <p style="margin: 0 0 10px 0; color: var(--muted); line-height: 1.6;">
                Upload a CSV containing columns like <strong>url</strong>, <strong>status_code</strong>, <strong>source_ip</strong>, <strong>user_agent</strong>, and optional labels/verdicts.
                Data stays local; once processed, you'll be redirected to the dashboard.
            </p>
        """,
        unsafe_allow_html=True,
    )
    file = st.file_uploader("CSV file", type="csv")
    st.markdown("</div>", unsafe_allow_html=True)

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
