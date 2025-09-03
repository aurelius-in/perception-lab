from __future__ import annotations

import time
from pathlib import Path

import streamlit as st
import requests


def get_logo_path() -> Path:
    # Resolve path to assets/pl-ani.gif relative to this file
    return Path(__file__).resolve().parents[1] / "assets" / "pl-ani.gif"


def inject_base_styles() -> None:
    st.markdown(
        """
        <style>
        /* App background */
        .stApp { background-color: #060E26; }

        /* Headings color */
        h1, h2, h3, h4, h5, h6 { color: #02ABC1 !important; }

        /* Top banner */
        .top-banner {
            width: 100%;
            background-color: #060E26;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 8px 0 12px 0;
        }
        .top-banner img { max-height: 64px; }

        /* Centering helpers */
        .center { display: flex; align-items: center; justify-content: center; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_splash(logo_path: Path, duration_seconds: float = 1.8) -> None:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("""<div class='center' style='height: 80vh'></div>""", unsafe_allow_html=True)
        col_left, col_center, col_right = st.columns([1, 2, 1])
        with col_center:
            st.image(str(logo_path), use_column_width=False)
    time.sleep(duration_seconds)
    placeholder.empty()


def render_top_banner(logo_path: Path) -> None:
    st.markdown(
        f"""
        <div class="top-banner">
            <img src="file://{logo_path.as_posix()}" alt="Perception Ops Lab" />
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(page_title="Perception Ops Lab", layout="wide")

    inject_base_styles()

    logo_path = get_logo_path()
    if not st.session_state.get("splash_done", False):
        show_splash(logo_path)
        st.session_state["splash_done"] = True
        st.rerun()

    render_top_banner(logo_path)

    st.title("Perception Ops Lab — Agentic (Cloud-First)")

    api_base = st.sidebar.text_input("API base URL", value="http://localhost:8000")
    st.sidebar.caption("Set FastAPI base URL")

    tab_run, tab_eval, tab_metrics, tab_reports, tab_fusion = st.tabs(
        ["Run", "Evaluate", "Metrics", "Reports", "Fusion"]
    )

    with tab_run:
        st.subheader("Run")
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            video = st.selectbox("Video", options=["data/samples/day.mp4", "data/samples/night.mp4"]) 
        with col2:
            profile = st.selectbox("Profile", options=["realtime", "accuracy"], index=0)
        with col3:
            start = st.button("Start")
            pause = st.button("Pause")
            reset = st.button("Reset")

        st.caption("Overlays and streaming will appear here in later steps.")
        if start:
            try:
                resp = requests.post(f"{api_base}/run_video", json={"video_path": video, "profile": profile}, timeout=5)
                st.success(f"Requested run: {resp.json()}")
            except Exception as e:
                st.warning(f"API not reachable yet: {e}")

    with tab_eval:
        st.subheader("Evaluate")
        dataset = st.text_input("Dataset (COCO JSON)", value="data/labels/demo_annotations.json")
        tasks = st.multiselect("Tasks", options=["det","seg","track","ocr"], default=["det"]) 
        if st.button("Run Eval"):
            try:
                resp = requests.post(f"{api_base}/evaluate", json={"dataset": dataset, "tasks": tasks}, timeout=10)
                st.json(resp.json())
            except Exception as e:
                st.warning(f"API not reachable yet: {e}")

    with tab_metrics:
        st.subheader("Metrics")
        st.markdown("View Prometheus metrics at `/metrics`. Grafana default: http://localhost:3000")
        if st.button("Fetch /metrics"):
            try:
                text = requests.get(f"{api_base}/metrics", timeout=5).text
                st.code(text)
            except Exception as e:
                st.warning(f"Metrics not available yet: {e}")
        st.markdown("---")
        st.subheader("Last JSON event")
        if st.button("Fetch last event"):
            try:
                last = requests.get(f"{api_base}/last_event", timeout=5).json()
                st.json(last)
            except Exception as e:
                st.warning(f"Last event not available: {e}")

    with tab_reports:
        st.subheader("Reports")
        run_id = st.text_input("Run ID", value="2025-09-02_12-00-00")
        if st.button("Generate PDF"):
            try:
                resp = requests.post(f"{api_base}/report", json={"run_id": run_id}, timeout=10)
                st.success(resp.json())
            except Exception as e:
                st.warning(f"API not reachable yet: {e}")

    with tab_fusion:
        st.subheader("Fusion")
        st.caption("KITTI projection viewer will be added here.")


if __name__ == "__main__":
    main()


