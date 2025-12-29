import streamlit as st
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
    toggle_val = st.toggle("Dark theme", value=st.session_state["theme"] == "Dark", key="theme_toggle_main")
    new_theme = "Dark" if toggle_val else "Light"
    if new_theme != st.session_state["theme"]:
        st.session_state["theme"] = new_theme
        apply_theme_from_session()

# Hero section
hero_section = st.container(key="hero_section")
with hero_section:
    st.markdown(
        """
        <div style="max-width: 960px; margin: 0 auto; text-align: center; padding: 24px 0 12px 0;">
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

# Overview card
content_section = st.container(key="content_section")
with content_section:
    st.markdown(
        """
        <div style="max-width: 900px; margin: 0 auto;">
            <div style="background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 20px; box-shadow: var(--shadow);">
                <div style="font-weight: 700; font-size: 1.1rem; margin-bottom: 10px;">Platform Overview</div>
                <p style="margin: 0; color: var(--muted); font-size: 1rem; line-height: 1.6;">
                    Unified log ingestion, layered detection (rules + ML), behavioral correlation, and SOC-ready reporting.
                    Built to accelerate threat triage and response while keeping analysts focused on what matters.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
