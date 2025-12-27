import streamlit as st, plotly.express as px
import plotly.graph_objects as go
import time
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
with st.spinner("Loading dashboard..."):
    time.sleep(0.5)

header_cols = st.columns([3, 1])
with header_cols[0]:
    st.title("Dashboard")
with header_cols[1]:
    st.markdown("")  # space for alignment
    if st.button("Successful Attacks", type="secondary", use_container_width=True):
        st.switch_page("pages/4_Successful_Attacks.py")

if "data" not in st.session_state:
    st.stop()

df = apply_pipeline(st.session_state["data"])

st.markdown("### Metrics")
metric_card = """
<div style="background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 16px 16px; box-shadow: var(--shadow);">
"""
metric_close = "</div>"

total_logs = len(df)
attacks = df["Final_Attack"].ne("Normal").sum() if "Final_Attack" in df else 0
successful_attacks = df["Final_Attack"].eq("Successful").sum() if "Final_Attack" in df else 0


def kpi_card(title, value, color):
    fig = go.Figure(
        go.Indicator(
            mode="number",
            value=value,
            number={"font": {"size": 42, "color": color}},
            title={"text": title, "font": {"size": 16, "color": "var(--muted)"}},
            domain={"x": [0, 1], "y": [0, 1]},
        )
    )
    fig.update_layout(
        height=140,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=20, b=0),
        transition={"duration": 600, "easing": "cubic-in-out"},
    )
    return fig

kpi_cols = st.columns(3)
kpi_cols[0].plotly_chart(
    kpi_card("Total Logs", total_logs, "var(--text)"),
    use_container_width=True,
    config={"displayModeBar": False},
)
kpi_cols[1].plotly_chart(
    kpi_card("Detected Attacks", attacks, "var(--high)"),
    use_container_width=True,
    config={"displayModeBar": False},
)
kpi_cols[2].plotly_chart(
    kpi_card("Successful Attacks", successful_attacks, "var(--primary)"),
    use_container_width=True,
    config={"displayModeBar": False},
)

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

st.markdown("### Traffic Overview")
st.markdown(
    metric_card + "<div style='margin-bottom: 8px; font-weight: 600;'>All Traffic</div>" + metric_close,
    unsafe_allow_html=True,
)


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
                    ("background-color", "rgba(21,33,52,0.85)"),
                    ("color", "var(--text)"),
                    ("border-color", "var(--border)"),
                    ("font-size", "0.95rem"),
                    ("font-weight", "700"),
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

    return styler

styled_df = console_style(df)
st.dataframe(styled_df, use_container_width=True)

chart_cols = st.columns(2)
with chart_cols[0]:
    st.markdown("#### Attack Distribution")
    attack_fig = px.bar(df[df["Final_Attack"] != "Normal"], x="Final_Attack")
    attack_fig.update_layout(
        transition={"duration": 700, "easing": "cubic-in-out"},
        margin=dict(l=10, r=10, t=30, b=10),
    )
    st.plotly_chart(attack_fig, use_container_width=True)

with chart_cols[1]:
    st.markdown("#### Priority Mix")
    priority_fig = px.pie(df, names="Priority")
    priority_fig.update_layout(transition={"duration": 700, "easing": "cubic-in-out"})
    st.plotly_chart(priority_fig, use_container_width=True)

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
