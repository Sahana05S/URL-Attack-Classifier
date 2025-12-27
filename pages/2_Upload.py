import streamlit as st, pandas as pd
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
with st.spinner("Loading upload..."):
    time.sleep(0.5)

st.title("Upload Logs")
st.markdown(
    "Upload URL access logs in CSV format. Expected columns include URL, source IP, user agent, timestamp, and any existing verdicts/labels for analysis."
)

file = st.file_uploader("Upload CSV", type="csv")
if file:
    df = pd.read_csv(file)
    st.session_state["data"] = df
    st.success("Logs uploaded successfully.")
    st.switch_page("pages/3_Dashboard.py")
