from __future__ import annotations

from base64 import b64encode
from pathlib import Path
import streamlit as st


BASE_CSS = Path("assets/style.css")
BG_IMAGE = Path("assets/Bg-1.jpg")


@st.cache_data(show_spinner=False)
def _bg_image_base64() -> str | None:
    if not BG_IMAGE.exists():
        return None
    return b64encode(BG_IMAGE.read_bytes()).decode("utf-8")


def apply_global_styles() -> None:
    """Inject global styles and (if present) the background image."""
    if BASE_CSS.exists():
        st.markdown(f"<style>{BASE_CSS.read_text()}</style>", unsafe_allow_html=True)

    # Fallback: inline the background image so it still renders if asset paths fail.
    encoded = _bg_image_base64()
    if encoded:
        st.markdown(
            f"""
            <style>
            section[data-testid="stAppViewContainer"] {{
              background:
                linear-gradient(rgba(6, 30, 41, 0.65), rgba(6, 30, 41, 0.65)),
                url("data:image/jpg;base64,{encoded}") center center / cover fixed no-repeat;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )


def top_navbar(active: str = "Home") -> None:
    """Render the top navbar using Streamlit columns."""

    auth_ok = bool(st.session_state.get("auth_ok"))

    def _go_home():
        st.switch_page("app.py")

    def _handle_protected(target: str, action: str):
        if auth_ok:
            st.switch_page(target)
        else:
            st.session_state.show_auth = True
            st.session_state["post_login_target"] = target
            st.switch_page("app.py")

    nav_cols = st.columns([1.8, 1, 1, 1, 1.1])

    nav_cols[0].markdown("**URL Attack Detection System**")

    if nav_cols[1].button(
        "Home",
        key="nav_home_btn",
        type="primary" if active == "Home" else "secondary",
        use_container_width=True,
    ):
        _go_home()

    if nav_cols[2].button(
        "Upload",
        key="nav_upload_btn",
        type="primary" if active == "Upload" else "secondary",
        use_container_width=True,
    ):
        _handle_protected("pages/2_Upload.py", "Upload")

    if nav_cols[3].button(
        "Dashboard",
        key="nav_dashboard_btn",
        type="primary" if active == "Dashboard" else "secondary",
        use_container_width=True,
    ):
        _handle_protected("pages/3_Dashboard.py", "Dashboard")

    auth_label = "Logout" if auth_ok else "Login / Sign Up"
    if nav_cols[4].button(
        auth_label,
        key="nav_auth_btn",
        type="primary" if active == "Auth" else "secondary",
        use_container_width=True,
    ):
        if auth_ok:
            st.session_state["auth_ok"] = False
            st.session_state["auth"] = {"logged_in": False, "user": None}
            st.session_state["user"] = None
            _go_home()
        else:
            st.session_state.show_auth = True
            st.session_state["post_login_target"] = None
