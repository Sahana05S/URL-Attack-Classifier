import streamlit as st
from pathlib import Path

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
    toggle_val = st.toggle("Dark theme", value=current_theme == "Dark", key="theme_toggle_home")
    new_theme = "Dark" if toggle_val else "Light"
    if new_theme != current_theme:
        st.session_state["theme"] = new_theme
        apply_theme_from_session()

# Hero Section
hero_section = st.container(key="hero_section")
with hero_section:
    st.markdown(
        """
        <div style="max-width: 960px; margin: 0 auto; text-align: center; padding: 16px 0 12px 0;">
            <div style="font-size: 2.2rem; font-weight: 800;">URL Attack Detection System</div>
            <div style="color: var(--muted); font-size: 1.05rem; margin-top: 8px;">
                Enterprise-grade detection, triage, and reporting for malicious URL activity across your estate.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Navigation / Actions
nav_section = st.container(key="nav_section")
with nav_section:
    action_cols = st.columns(2)
    with action_cols[0]:
        if st.button("Upload Logs", type="primary", use_container_width=True):
            st.switch_page("pages/2_Upload.py")
    with action_cols[1]:
        if st.button("View Dashboard", type="secondary", use_container_width=True):
            st.switch_page("pages/3_Dashboard.py")

# Main Content
content_section = st.container(key="content_section")
with content_section:
    row1 = st.columns([2, 1])
    with row1[0]:
        st.markdown(
            """
            <div style="background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 18px 20px; box-shadow: var(--shadow);">
                <div style="font-weight: 700; font-size: 1.15rem; margin-bottom: 10px;">System Overview</div>
                <p style="margin: 0; color: var(--muted); font-size: 1rem; line-height: 1.65;">
                    Automated ingestion and scoring of URL activity with layered detections (rules + ML), enrichment, and SOC-ready reporting. Designed for fast triage, analyst clarity, and measurable risk reduction.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with row1[1]:
        st.markdown(
            """
            <div style="background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 18px 20px; box-shadow: var(--shadow);">
                <div style="font-weight: 700; font-size: 1.1rem; margin-bottom: 12px;">System Status</div>
                <div style="display: flex; flex-direction: column; gap: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 12px; border-radius: 12px; background: rgba(83, 194, 127, 0.15); border: 1px solid rgba(83, 194, 127, 0.35);">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <span style="width: 10px; height: 10px; border-radius: 50%; background: var(--low);"></span>
                            <span>Inference Engine</span>
                        </div>
                        <strong style="color: var(--low);">Ready</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 12px; border-radius: 12px; background: rgba(231, 165, 77, 0.12); border: 1px solid rgba(231, 165, 77, 0.35);">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <span style="width: 10px; height: 10px; border-radius: 50%; background: var(--medium);"></span>
                            <span>Data Pipeline</span>
                        </div>
                        <strong style="color: var(--medium);">Waiting for Logs</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 12px; border-radius: 12px; background: rgba(79, 156, 255, 0.12); border: 1px solid rgba(79, 156, 255, 0.35);">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <span style="width: 10px; height: 10px; border-radius: 50%; background: var(--primary);"></span>
                            <span>Reporting</span>
                        </div>
                        <strong style="color: var(--primary);">Ready</strong>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    feature_cols = st.columns(3)
    features = [
        ("Detection Engine", "Hybrid rules + ML scoring with priority tagging and suppression controls."),
        ("Enrichment & Context", "WHOIS, IP reputation, URL decomposition, and correlation across sessions."),
        ("Operations Ready", "Dashboards, exports, and status visibility built for SOC workflows."),
    ]

    for col, (title, desc) in zip(feature_cols, features):
        with col:
            st.markdown(
                f"""
                <div style="background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 16px 16px; box-shadow: var(--shadow); height: 100%;">
                    <div style="font-weight: 700; margin-bottom: 8px;">{title}</div>
                    <p style="margin: 0; color: var(--muted); line-height: 1.6;">{desc}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
