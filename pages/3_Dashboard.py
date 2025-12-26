import streamlit as st, plotly.express as px
from pipeline import apply_pipeline

with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

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

# Metrics row
total_logs = len(df)
attacks = df["Final_Attack"].ne("Normal").sum() if "Final_Attack" in df else 0
successful_attacks = df["Final_Attack"].eq("Successful").sum() if "Final_Attack" in df else 0

metric_cols = st.columns(3)
metric_cols[0].metric("Total Logs", f"{total_logs:,}")
metric_cols[1].metric("Attacks", f"{attacks:,}")
metric_cols[2].metric("Successful", f"{successful_attacks:,}")

st.markdown("### Traffic Overview")
st.dataframe(df, use_container_width=True)

chart_cols = st.columns(2)
with chart_cols[0]:
    st.markdown("#### Attack Distribution")
    st.plotly_chart(
        px.bar(df[df["Final_Attack"] != "Normal"], x="Final_Attack"),
        use_container_width=True,
    )

with chart_cols[1]:
    st.markdown("#### Priority Mix")
    st.plotly_chart(px.pie(df, names="Priority"), use_container_width=True)
