import streamlit as st, plotly.express as px
from pathlib import Path
from pipeline import apply_pipeline

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
    toggle_val = st.toggle("Dark theme", value=current_theme == "Dark", key="theme_toggle_dashboard")
    new_theme = "Dark" if toggle_val else "Light"
    if new_theme != current_theme:
        st.session_state["theme"] = new_theme
        apply_theme_from_session()

if "data" not in st.session_state:
    st.stop()

df = apply_pipeline(st.session_state["data"])

# 1. Title row
title_section = st.container()
with title_section:
    header_cols = st.columns([3, 1])
    header_cols[0].title("Dashboard")
    with header_cols[1]:
        if st.button("Successful Attacks", type="secondary", use_container_width=True):
            st.switch_page("pages/4_Successful_Attacks.py")

# 2. Metrics row
metrics_section = st.container()
with metrics_section:
    total_logs = len(df)
    attacks = df["Final_Attack"].ne("Normal").sum() if "Final_Attack" in df else 0
    successful_attacks = df["Final_Attack"].eq("Successful").sum() if "Final_Attack" in df else 0
    mcols = st.columns(3)
    mcols[0].metric("Total Logs", f"{total_logs:,}")
    mcols[1].metric("Detected Attacks", f"{attacks:,}")
    mcols[2].metric("Successful", f"{successful_attacks:,}")

# 3. Traffic table
table_section = st.container()
with table_section:
    st.markdown("### Traffic Overview")
    st.caption("All Traffic (processed pipeline output)")

    def console_style(dataframe):
        def highlight_rows(row):
            styles = [""] * len(row)
            is_high = str(row.get("Priority", "")).lower() == "high"
            is_success = str(row.get("Final_Attack", "")).lower() == "successful"
            if is_success:
                styles = [
                    "background-color: rgba(79,156,255,0.12); color: #e8f0ff; font-weight: 600;"
                ] * len(row)
            elif is_high:
                styles = [
                    "background-color: rgba(224,85,85,0.14); color: #fdfdff; font-weight: 600;"
                ] * len(row)
            return styles

        def priority_style(value):
            key = str(value).lower()
            if key == "high":
                return "background-color: #e05555; color: #ffffff; font-weight: 700;"
            if key == "medium":
                return "background-color: #e7a54d; color: #000000; font-weight: 700;"
            if key == "low":
                return "background-color: #53c27f; color: #ffffff; font-weight: 700;"
            return ""

        def attack_style(value):
            key = str(value).lower()
            if key in ["sql injection", "sqli"]:
                return "background-color: rgba(224,85,85,0.18); color: #e05555; font-weight: 700;"
            if key in ["xss"]:
                return "background-color: rgba(255,204,0,0.2); color: #ffcc00; font-weight: 700;"
            if key in ["directory traversal"]:
                return "background-color: rgba(83,194,127,0.2); color: #36b26e; font-weight: 700;"
            if key in ["command injection"]:
                return "background-color: rgba(177,59,255,0.18); color: #b13bff; font-weight: 700;"
            if key in ["ssrf"]:
                return "background-color: rgba(71,19,150,0.22); color: #471396; font-weight: 700;"
            if key == "normal":
                return "color: var(--muted);"
            return ""

        styler = dataframe.style.set_properties(
            **{
                "font-family": '"SFMono-Regular","Consolas","Menlo","monospace"',
                "border-color": "var(--border)",
                "font-size": "0.95rem",
                "line-height": "1.5",
            }
        ).set_table_styles(
            [
                {
                    "selector": "th",
                    "props": [
                        ("background-color", "var(--card)"),
                        ("color", "var(--text)"),
                        ("border-color", "var(--border)"),
                        ("font-size", "0.95rem"),
                        ("font-weight", "700"),
                        ("position", "sticky"),
                        ("top", "0"),
                        ("z-index", "2"),
                    ],
                },
                {
                    "selector": "tbody tr:hover td",
                    "props": [
                        ("background-color", "rgba(79,156,255,0.08)"),
                        ("color", "var(--text)"),
                    ],
                }
            ]
        )

        styler = styler.apply(highlight_rows, axis=1)

        if "Priority" in dataframe.columns:
            styler = styler.applymap(priority_style, subset=["Priority"])
        if "Final_Attack" in dataframe.columns:
            styler = styler.applymap(attack_style, subset=["Final_Attack"])

        return styler

    st.dataframe(console_style(df), use_container_width=True)

# 4. Charts row
charts_section = st.container()
with charts_section:
    chart_cols = st.columns(2)
    with chart_cols[0]:
        st.markdown("#### Attack Distribution")
        attack_fig = px.bar(df[df["Final_Attack"] != "Normal"], x="Final_Attack")
        attack_fig.update_layout(
            transition={"duration": 700, "easing": "cubic-in-out"},
            margin=dict(l=10, r=10, t=30, b=10),
        )
        attack_fig.update_traces(base=0)
        st.plotly_chart(attack_fig, use_container_width=True)

    with chart_cols[1]:
        st.markdown("#### Priority Mix")
        priority_fig = px.pie(df, names="Priority")
        priority_fig.update_layout(transition={"duration": 700, "easing": "cubic-in-out"})
        priority_fig.update_traces(sort=False)
        st.plotly_chart(priority_fig, use_container_width=True)
