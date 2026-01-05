import streamlit as st
from pathlib import Path
from auth_db import authenticate, create_user, init_db
from core.ui_shell import apply_global_styles, top_navbar

st.set_page_config(page_title="URL Attack Detection System", layout="wide", initial_sidebar_state="collapsed")

# Init auth/db
init_db()
st.session_state.setdefault("auth", {"logged_in": False, "user": None})
st.session_state.setdefault("auth_ok", False)
st.session_state.setdefault("user", None)
st.session_state.setdefault("show_auth", False)
st.session_state.setdefault("post_login_target", None)

apply_global_styles()


def is_logged_in() -> bool:
    return bool(st.session_state.get("auth_ok"))


@st.dialog("Account")
def auth_modal():
    tabs = st.tabs(["Login", "Sign Up"])

    with tabs[0]:
        email = st.text_input("Email", key="root_login_email")
        password = st.text_input("Password", type="password", key="root_login_password")
        if st.button("Login", use_container_width=True, key="root_login_button"):
            ok, msg, user = authenticate(email, password)
            if ok:
                st.session_state.auth = {"logged_in": True, "user": user}
                st.session_state["auth_ok"] = True
                st.session_state["user"] = user
                st.session_state.show_auth = False
                st.success("Logged in successfully")
                target = st.session_state.pop("post_login_target", None)
                if target:
                    st.switch_page(target)
                else:
                    st.rerun()
            else:
                st.error(msg)

    with tabs[1]:
        name = st.text_input("Name", key="root_signup_name")
        email = st.text_input("Email", key="root_signup_email")
        pw1 = st.text_input("Password", type="password", key="root_signup_pw1")
        pw2 = st.text_input("Confirm Password", type="password", key="root_signup_pw2")
        if st.button("Create Account", use_container_width=True, key="root_signup_button"):
            if pw1 != pw2:
                st.error("Passwords do not match")
            else:
                ok, msg = create_user(name, email, pw1)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)


# Navbar
top_navbar("Home")

# Home content
hero_html = """
<div class="glass-card soft hero-card stack">
  <div class="pill">URL Security Platform</div>
  <div style="font-size: 2.2rem; font-weight: 800;">URL Attack Detection System</div>
  <div class="muted" style="font-size: 1.05rem;">
    Enterprise-grade detection, triage, and reporting for malicious URL activity across your environment.
  </div>
</div>
"""
st.markdown(hero_html, unsafe_allow_html=True)

# CTA band
cta_container = st.container()
with cta_container:
    cta_cols = st.columns(2)
    with cta_cols[0]:
        if st.button("Upload Logs", type="primary", use_container_width=True):
            if is_logged_in():
                st.switch_page("pages/2_Upload.py")
            else:
                st.session_state.show_auth = True
                st.session_state["post_login_target"] = "pages/2_Upload.py"
    with cta_cols[1]:
        if st.button("View Dashboard", type="secondary", use_container_width=True):
            if is_logged_in():
                st.switch_page("pages/3_Dashboard.py")
            else:
                st.session_state.show_auth = True
                st.session_state["post_login_target"] = "pages/3_Dashboard.py"

# Overview
overview_html = """
<div class="glass-card stack">
  <div class="card-title">Platform Overview</div>
  <div class="muted">
    Unified log ingestion, layered detection (rules + ML), behavioral correlation, and SOC-ready reporting.
    Built to accelerate threat triage and response while keeping analysts focused on what matters.
  </div>
</div>
"""
st.markdown(overview_html, unsafe_allow_html=True)

# Features
feature_cards = [
    ("Detection Engine", "Hybrid rules + ML scoring with priority tagging and suppression controls."),
    ("Enrichment & Context", "WHOIS, IP reputation, URL decomposition, and correlation across sessions."),
    ("Operations Ready", "Dashboards, exports, and status visibility built for SOC workflows."),
]
feature_html = '<div class="card-grid">'
for title, desc in feature_cards:
    feature_html += f"""
    <div class="glass-card">
      <div class="card-title">{title}</div>
      <div class="muted">{desc}</div>
    </div>
    """
feature_html += "</div>"
st.markdown(feature_html, unsafe_allow_html=True)

# Show auth modal if requested
if st.session_state.get("show_auth") and not is_logged_in():
    auth_modal()
