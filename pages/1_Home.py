import streamlit as st
import time
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

apply_theme_from_session()

# Smooth transition
with st.spinner("Loading home..."):
    time.sleep(0.5)

# Hero
left, center, right = st.columns([1, 2, 1])
with center:
    st.markdown(
        """
        <div style="text-align: center; padding: 16px 0 8px 0;">
            <div style="font-size: 2.2rem; font-weight: 800;">URL Attack Detection System</div>
            <div style="color: var(--muted); font-size: 1.05rem; margin-top: 8px;">
                Enterprise-grade detection, triage, and reporting for malicious URL activity across your estate.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    action_cols = st.columns(2)
    with action_cols[0]:
        if st.button("Upload Logs", type="primary", use_container_width=True):
            st.switch_page("pages/2_Upload.py")
    with action_cols[1]:
        if st.button("View Dashboard", type="secondary", use_container_width=True):
            st.switch_page("pages/3_Dashboard.py")

st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

# System overview + status
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

st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

# Key features
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
