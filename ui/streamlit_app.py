from __future__ import annotations

import time
from pathlib import Path

import streamlit as st
import requests
import threading
import json as _json
from urllib.parse import urlencode


def get_logo_path() -> Path:
    # Resolve path to assets/logo.svg relative to this file
    return Path(__file__).resolve().parents[1] / "ui" / "assets" / "logo.svg"


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
        .stButton>button { transition: all 200ms ease-in-out; border-radius: 8px; }

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
            <img src="file://{logo_path.as_posix()}" alt="PerceptionLab" />
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

        st.markdown("### Overlays")
        show_boxes = st.checkbox("Boxes", value=True)
        show_tracks = st.checkbox("Tracks", value=True)
        show_ocr = st.checkbox("OCR", value=True)

        st.markdown("### Telemetry")
        fps_placeholder = st.empty()

        st.caption("WebSocket stream (stub) will print events below.")
        log_box = st.empty()

        def _run_ws():
            try:
                from websocket import create_connection
            except Exception as e:  # dependency missing
                log_box.warning(f"websocket-client not installed: {e}")
                return
            try:
                qs = urlencode({"video_path": video, "profile": profile})
                ws = create_connection(f"{api_base.replace('http', 'ws')}/ws/run_video?{qs}")
                messages = []
                while True:
                    msg = ws.recv()
                    if not msg:
                        break
                    try:
                        ev = _json.loads(msg)
                        messages.append(ev)
                        if ev.get("fps"):
                            fps_placeholder.metric("FPS", f"{ev['fps']:.1f}")
                    except Exception:
                        messages.append({"raw": msg})
                    # show only last few
                    log_box.json(messages[-5:])
            except Exception as e:
                log_box.warning(f"WS error: {e}")

        if start:
            threading.Thread(target=_run_ws, daemon=True).start()

        st.markdown("---")
        st.subheader("Single-frame detection test")
        uploaded = st.file_uploader("Upload image (jpg/png)", type=["jpg","jpeg","png"])
        if uploaded and st.button("Run /run_frame"):
            import base64
            img_b64 = base64.b64encode(uploaded.read()).decode("utf-8")
            try:
                resp = requests.post(f"{api_base}/run_frame", json={"image_b64": img_b64, "profile": profile}, timeout=30)
                data = resp.json()
                col_a, col_b = st.columns(2)
                with col_a:
                    st.caption("Response JSON")
                    st.json(data)
                with col_b:
                    if data.get("annotated_b64"):
                        st.caption("Annotated")
                        st.image(data["annotated_b64"], caption="Overlay", use_column_width=True)
                    else:
                        st.info("No annotated image returned.")
            except Exception as e:
                st.warning(f"/run_frame failed: {e}")

        st.markdown("---")
        st.subheader("Realtime vs Accuracy (single image)")
        uploaded_cmp = st.file_uploader("Upload image for compare", type=["jpg","jpeg","png"], key="cmp")
        if uploaded_cmp and st.button("Compare profiles"):
            import base64
            img_bytes = uploaded_cmp.read()
            img_b64 = base64.b64encode(img_bytes).decode("utf-8")
            try:
                rt = requests.post(f"{api_base}/run_frame", json={"image_b64": img_b64, "profile": "realtime"}, timeout=30).json()
                acc = requests.post(f"{api_base}/run_frame", json={"image_b64": img_b64, "profile": "accuracy"}, timeout=30).json()
                from streamlit_image_comparison import image_comparison
                if rt.get("annotated_b64") and acc.get("annotated_b64"):
                    image_comparison(
                        img1=rt["annotated_b64"],
                        img2=acc["annotated_b64"],
                        label1="Realtime",
                        label2="Accuracy",
                        width=700,
                    )
            except Exception as e:
                st.warning(f"Compare failed: {e}")

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

        st.markdown("---")
        if st.button("Generate report for last run"):
            try:
                last = requests.get(f"{api_base}/last_event", timeout=5).json()
                last_run = last.get("run_id")
                if not last_run:
                    st.info("No recent runs.")
                else:
                    resp = requests.post(f"{api_base}/report", json={"run_id": last_run}, timeout=20).json()
                    st.success(resp)
            except Exception as e:
                st.warning(f"Failed to build report: {e}")

    with tab_fusion:
        st.subheader("Fusion")
        st.caption("KITTI LiDAR → camera projection (single frame)")
        base = st.text_input("KITTI frame dir", value="data/kitti_frame")
        if st.button("Project points"):
            try:
                from app.pipelines.fusion_projection import load_kitti_and_project
                from PIL import Image
                import numpy as np
                img_path = Path(base) / "image.png"
                if not img_path.exists():
                    st.warning("Missing image.png in the specified directory.")
                else:
                    points, pixels = load_kitti_and_project(Path(base))
                    im = Image.open(img_path)
                    arr = np.array(im).copy()
                    # Draw small dots
                    for x, y in pixels.astype(int):
                        if 0 <= y < arr.shape[0] and 0 <= x < arr.shape[1]:
                            arr[y, x] = [2, 171, 193]
                    st.image(arr, caption="Projected points", use_column_width=True)
            except Exception as e:
                st.warning(f"Fusion projection failed: {e}")


if __name__ == "__main__":
    main()


