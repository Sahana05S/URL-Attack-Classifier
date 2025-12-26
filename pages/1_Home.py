import streamlit as st

with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

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

# Content cards
card_cols = st.columns(2)
with card_cols[0]:
    st.markdown(
        """
        <div style="background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 18px 20px; box-shadow: var(--shadow);">
            <div style="font-weight: 700; font-size: 1.1rem; margin-bottom: 10px;">Platform Overview</div>
            <p style="margin: 0; color: var(--muted); font-size: 1rem; line-height: 1.6;">
                Unified URL ingestion, layered rules and ML scoring, behavioral correlation, and SOC-ready reporting to accelerate investigation and response.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with card_cols[1]:
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
