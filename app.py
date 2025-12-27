import streamlit as st
import time
from pathlib import Path

st.set_page_config(page_title="URL Attack Detection System", layout="wide")

# Theming helpers
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

    if theme == "Light":
        background_css = """
        body {
            background: radial-gradient(120% 120% at 14% 18%, #f6f9ff 0%, #eef3ff 40%, #e4ecff 100%);
        }
        .block-container {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.92), rgba(244, 248, 255, 0.9));
            border-radius: 20px;
            padding: 32px;
            box-shadow: 0 18px 56px rgba(31, 63, 125, 0.18);
        }
        """
    else:
        background_css = """
        body {
            background: radial-gradient(120% 120% at 15% 20%, #0b1224 0%, #0c1328 35%, #080f1f 55%, #060b17 100%);
        }
        .block-container {
            background: linear-gradient(135deg, rgba(19, 28, 48, 0.55), rgba(8, 15, 31, 0.65));
            border-radius: 20px;
            padding: 32px;
            box-shadow: 0 24px 64px rgba(0, 0, 0, 0.35);
        }
        """
    st.markdown(f"<style>{background_css}</style>", unsafe_allow_html=True)


if "theme" not in st.session_state:
    st.session_state["theme"] = "Dark"

theme_choice = st.radio(
    "Theme",
    options=["Dark", "Light"],
    horizontal=True,
    index=0 if st.session_state["theme"] == "Dark" else 1,
)
if theme_choice != st.session_state["theme"]:
    st.session_state["theme"] = theme_choice

apply_theme_from_session()

# Smooth transition
with st.spinner("Preparing view..."):
    time.sleep(0.5)

# Top navigation
nav_cols = st.columns([1, 1, 1, 6])
with nav_cols[0]:
    st.page_link("pages/1_Home.py", label="Home")
with nav_cols[1]:
    st.page_link("pages/2_Upload.py", label="Upload")
with nav_cols[2]:
    st.page_link("pages/3_Dashboard.py", label="Dashboard")

# Hero section
_, hero_center, _ = st.columns([1, 2, 1])
with hero_center:
    st.markdown(
        """
        <div style="text-align: center; padding: 24px 0 8px 0;">
            <div style="font-size: 2.4rem; font-weight: 800;">URL Attack Detection System</div>
            <div style="color: var(--muted); font-size: 1.05rem; margin-top: 10px;">
                Enterprise-grade detection, triage, and reporting for malicious URL activity across your environment.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    cta_cols = st.columns(2)
    with cta_cols[0]:
        if st.button("Upload Logs", type="primary", use_container_width=True):
            st.switch_page("pages/2_Upload.py")
    with cta_cols[1]:
        if st.button("View Dashboard", type="secondary", use_container_width=True):
            st.switch_page("pages/3_Dashboard.py")

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# Overview card
card = st.columns([1, 2, 1])[1]
with card:
    st.markdown(
        """
        <div style="background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 20px; box-shadow: var(--shadow);">
            <div style="font-weight: 700; font-size: 1.1rem; margin-bottom: 10px;">Platform Overview</div>
            <p style="margin: 0; color: var(--muted); font-size: 1rem; line-height: 1.6;">
                Unified log ingestion, layered detection (rules + ML), behavioral correlation, and SOC-ready reporting.
                Built to accelerate threat triage and response while keeping analysts focused on what matters.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
