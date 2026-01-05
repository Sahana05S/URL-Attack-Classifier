import streamlit as st


def render_navbar(active: str = "Home") -> None:
    """
    Render a fixed top navigation bar. Call this at the very top of every page.
    """
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"],
        [data-testid="collapsedControl"] {
          display: none !important;
        }
        #MainMenu, footer { display: none !important; }
        .navbar {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          z-index: 999;
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 14px 48px;
          background: rgba(6, 30, 41, 0.55);
          backdrop-filter: blur(14px);
          -webkit-backdrop-filter: blur(14px);
          border-bottom: 1px solid rgba(255,255,255,0.08);
        }
        .nav-center {
          display: flex;
          gap: 18px;
          align-items: center;
          justify-content: center;
        }
        .nav-right {
          display: flex;
          align-items: center;
          justify-content: flex-end;
        }
        .nav-btn .stButton > button {
          background: var(--secondary, rgba(29, 84, 109, 0.55));
          color: var(--text, #F3F4F4);
          border-radius: 14px;
          padding: 8px 22px;
          margin: 0 !important;
          border: 1px solid var(--accent, rgba(255,255,255,0.1));
        }
        .nav-btn .stButton > button:hover {
          border-color: var(--accent, rgba(255,255,255,0.3));
        }
        .nav-spacer {
          height: 64px;
          width: 100%;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    def _authenticated() -> bool:
        return bool(st.session_state.get("authenticated"))

    def _open_login_modal():
        st.session_state.show_auth = True

    def _go_home():
        st.switch_page("app.py")

    def _go_upload():
        if _authenticated():
            st.switch_page("pages/2_Upload.py")
        else:
            _open_login_modal()

    def _go_dashboard():
        if _authenticated():
            st.switch_page("pages/3_Dashboard.py")
        else:
            _open_login_modal()

    st.markdown('<div class="navbar">', unsafe_allow_html=True)
    brand_col, center_col, right_col = st.columns([1.6, 2.6, 1.2])

    with brand_col:
        st.markdown("**URL Attack Detection System**")

    with center_col:
        st.markdown('<div class="nav-center nav-btn">', unsafe_allow_html=True)
        if st.button("Home", key="nav_home_btn"):
            _go_home()
        if st.button("Upload", key="nav_upload_btn"):
            _go_upload()
        if st.button("Dashboard", key="nav_dashboard_btn"):
            _go_dashboard()
        st.markdown("</div>", unsafe_allow_html=True)

    with right_col:
        st.markdown('<div class="nav-right nav-btn">', unsafe_allow_html=True)
        if _authenticated():
            if st.button("Logout", key="nav_logout_button"):
                st.session_state.auth = {"logged_in": False, "user": None}
                st.session_state["authenticated"] = False
                st.rerun()
        else:
            if st.button("Login / Sign Up", key="nav_login_modal_button"):
                _open_login_modal()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<div class="nav-spacer"></div>', unsafe_allow_html=True)
