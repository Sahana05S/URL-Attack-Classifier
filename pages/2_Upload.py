import streamlit as st, pandas as pd

with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("Upload Logs")
file = st.file_uploader("Upload CSV", type="csv")
if file:
    df = pd.read_csv(file)
    st.session_state["data"] = df
    st.success("Uploaded")
    if st.button("View Dashboard", type="primary"):
        st.switch_page("pages/3_Dashboard.py")
