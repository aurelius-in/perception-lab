from __future__ import annotations

import time
from pathlib import Path
import os

import streamlit as st
import requests
import threading
import json as _json
from urllib.parse import urlencode


def get_logo_path() -> Path:
    # Resolve path to assets/pl-ani.gif relative to this file
    return Path(__file__).resolve().parents[1] / "assets" / "pl-ani.gif"


def inject_base_styles() -> None:
    st.markdown(
        """
        <style>
        /* App background */
        .stApp { background-color: #060F25; }
        /* Remove default top gaps so banner is flush */
        [data-testid="stHeader"] { display: none; }
        .block-container { padding-top: 0 !important; }

        /* Headings color */
        h1, h2, h3, h4, h5, h6 { color: #02ABC1 !important; }

        /* Top banner */
        .top-banner {
            width: 100%;
            background-color: #060F25;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 0;
            margin: 0;
        }
        .top-banner img { max-height: 192px; display: block; }
        .stButton>button { transition: all 200ms ease-in-out; border-radius: 8px; }
        .card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07); padding: 12px 14px; border-radius: 10px; }
        .sticky-hud { position: sticky; top: 6px; z-index: 100; background: rgba(6,15,37,0.85); backdrop-filter: blur(4px); padding: 6px 10px; border-radius: 8px; border: 1px solid rgba(2,171,193,0.2); }

        /* Centering helpers */
        .center { display: flex; align-items: center; justify-content: center; }

        /* Hotkeys hint */
        .hotkeys { color: #8fbac0; font-size: 12px; }

        /* Tabs: larger, distinct, high-contrast */
        .stTabs { margin-top: 6px; }
        .stTabs [data-baseweb="tab-list"] {
            display: flex;
            gap: 14px;
            justify-content: space-between;
            border-bottom: 1px solid rgba(255,255,255,0.08);
            padding-bottom: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            font-family: "Segoe UI", "Inter", system-ui, -apple-system, sans-serif;
            font-weight: 800;
            font-size: 1.45rem; /* larger */
            letter-spacing: 0.015em;
            color: #cfeaf0;
            padding: 14px 20px;
            border-radius: 14px 14px 0 0;
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.12);
            box-shadow: 0 2px 4px rgba(0,0,0,0.15) inset;
            transition: all 160ms ease-in-out;
            flex: 1 1 0;
            text-align: center;
            min-width: 0;
        }
        .stTabs [data-baseweb="tab"]:hover {
            color: #e6fbfe;
            background: rgba(2,171,193,0.12);
            border-color: rgba(2,171,193,0.35);
        }
        .stTabs [aria-selected="true"] {
            color: #02ABC1 !important;
            background: linear-gradient(180deg, rgba(2,171,193,0.22), rgba(2,171,193,0.06));
            border-color: rgba(2,171,193,0.55);
            box-shadow: 0 0 0 1px rgba(2,171,193,0.35), 0 8px 18px rgba(2,171,193,0.16);
        }
        .stTabs [data-baseweb="tab"]:focus-visible {
            outline: none;
            box-shadow: 0 0 0 2px rgba(2,171,193,0.55);
        }

        /* Hide image fullscreen popout control */
        div[data-testid="stImage"] button { display: none !important; }

        /* GIF grid and cards: responsive, full-width, wrap to second row if needed */
        .gif-grid { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; width: 100%; }
        .gif-card {
            background: rgba(0,0,0,0.35);
            border: 1px solid #ffffff;
            border-radius: 8px;
            padding: 8px;        /* inner padding */
            display: flex;
            flex-direction: column;
            align-items: center;
            width: clamp(200px, 16.5vw, 300px);
        }
        .gif-card img { display: block; width: 100%; height: auto; }
        .gif-card .gif-cap { color: #cfeaf0; font-size: 12px; margin-top: 8px; }
        .gif-card .gif-title { color: #e6fbfe; font-size: 1.15rem; font-weight: 800; text-align: center; }
        .gif-card .gif-sub { color: #cfeaf0; font-size: 1.0rem; font-weight: 700; text-align: center; }
        .gif-card .gif-desc { color: #9fc7ce; font-size: 0.95rem; margin-top: 2px; text-align: center; }
        .gif-card .gif-fn { color: #9fc7ce; font-size: 0.85rem; margin-top: 8px; word-break: break-all; text-align: center; }
        .carousel-frame { border: 1px solid #ffffff; border-radius: 10px; padding: 12px 16px; margin-top: 8px; }
        .carousel-row { display: flex; gap: 16px; justify-content: center; align-items: stretch; }
        .gif-card.highlight { border: 2px solid #ffffff; box-shadow: 0 0 0 2px rgba(255,255,255,0.12) inset; }
        .carousel-ctrl { display: flex; justify-content: center; align-items: center; gap: 14px; margin-top: 8px; }
        .carousel-ctrl .stButton>button { font-weight: 700; padding: 8px 16px; }

        /* Carousel arrows - larger, adjacent to card */
        .arrow-col button {
            font-size: 36px !important;
            padding: 18px 14px !important;
            height: 100% !important;
            width: 100% !important;
        }
        .gif-card .gif-desc { color: #9fc7ce; font-size: 12px; margin-top: 6px; text-align: center; }

        /* Soft edge fade and transparency for logos */
        .splash-logo {
            width: 70vw;
            max-width: 1600px;
            opacity: 0.8;
            /* Deeper, softer fade */
            -webkit-mask-image: radial-gradient(circle at 50% 50%, rgba(0,0,0,1) 35%, rgba(0,0,0,0.5) 60%, rgba(0,0,0,0.25) 80%, rgba(0,0,0,0) 100%);
                    mask-image: radial-gradient(circle at 50% 50%, rgba(0,0,0,1) 35%, rgba(0,0,0,0.5) 60%, rgba(0,0,0,0.25) 80%, rgba(0,0,0,0) 100%);
        }
        .banner-logo {
            max-height: 192px;
            opacity: 0.85;
            -webkit-mask-image: radial-gradient(circle at 50% 50%, rgba(0,0,0,1) 50%, rgba(0,0,0,0.45) 75%, rgba(0,0,0,0.18) 90%, rgba(0,0,0,0) 100%);
                    mask-image: radial-gradient(circle at 50% 50%, rgba(0,0,0,1) 50%, rgba(0,0,0,0.45) 75%, rgba(0,0,0,0.18) 90%, rgba(0,0,0,0) 100%);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_splash(logo_path: Path, duration_seconds: float = 10.0) -> None:
    import base64
    placeholder = st.empty()
    with placeholder.container():
        try:
            b64 = base64.b64encode(logo_path.read_bytes()).decode("utf-8")
            img_src = f"data:image/gif;base64,{b64}"
        except Exception:
            img_src = ""
        st.markdown(
            f"""
            <div class='center' style='height: 90vh; background-color: #060F25;'>
              <img class="splash-logo" src="{img_src}" alt="PerceptionLab" />
            </div>
            """,
            unsafe_allow_html=True,
        )
    time.sleep(duration_seconds)
    placeholder.empty()


def render_top_banner(logo_path: Path) -> None:
    import base64
    try:
        b64 = base64.b64encode(logo_path.read_bytes()).decode("utf-8")
        src = f"data:image/gif;base64,{b64}"
    except Exception:
        src = ""
    st.markdown(
        f"""
        <div class="top-banner">
            <img class="banner-logo" src="{src}" alt="PerceptionLab" />
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(page_title="Perception Ops Lab", layout="wide", initial_sidebar_state="collapsed")

    inject_base_styles()

    # API base default + connectivity badge
    def _default_api_base() -> str:
        return os.getenv("API_BASE_URL", "http://localhost:8000")

    if "api_base" not in st.session_state:
        st.session_state.api_base = _default_api_base()

    def _ping_api(base: str) -> bool:
        try:
            r = requests.get(f"{base}/health", timeout=2)
            return r.ok
        except Exception:
            return False

    logo_path = get_logo_path()
    if not st.session_state.get("splash_done", False):
        show_splash(logo_path)
        st.session_state["splash_done"] = True
        st.rerun()

    render_top_banner(logo_path)

    # Connection badge row (small)
    _ok = _ping_api(st.session_state.api_base)
    _badge = "🟢 Connected" if _ok else "🔴 Offline"
    st.markdown(
        f"""
        <div style="display:flex;justify-content:flex-end;align-items:center;font-size:12px;opacity:.9;">
          <span>{_badge}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Inject minimal JS hotkeys for hints (Streamlit limitation for full control)
    st.markdown(
        """
        <script>
        // Add tooltip to the sidebar toggle button
        function setSidebarToggleTitle(){
          const candidates = [
            document.querySelector('button[aria-label="Main menu"]'),
            document.querySelector('button[title]'),
            document.querySelector('[data-testid="collapsedControl"] button'),
            document.querySelector('header button')
          ].filter(Boolean);
          if (candidates.length > 0) {
            candidates[0].setAttribute('title', 'Advanced Settings');
          }
        }
        document.addEventListener('DOMContentLoaded', setSidebarToggleTitle);
        setTimeout(setSidebarToggleTitle, 1000);

        document.addEventListener('keydown', function(e) {
          if (e.code === 'Space') { console.log('Toggle play/pause (stub)'); e.preventDefault(); }
          if (e.code === 'ArrowLeft') { console.log('Seek backward (stub)'); }
          if (e.code === 'ArrowRight') { console.log('Seek forward (stub)'); }
        });
        </script>
        """,
        unsafe_allow_html=True,
    )

    # Advanced settings (collapsed)
    with st.sidebar.expander("Settings (Advanced)", expanded=False):
        ENVIRONMENTS = {
            "Local": "http://localhost:8000",
            "Docker (compose network)": "http://api:8000",
            # "Remote": "https://your-remote-api.example.com",
        }
        env_choice = st.selectbox("Environment", list(ENVIRONMENTS.keys()), index=0)
        st.session_state.api_base = ENVIRONMENTS[env_choice]
        manual = st.text_input("Override base URL", value=st.session_state.api_base)
        st.session_state.api_base = manual
        st.caption("Changes apply immediately.")

    api_base = st.session_state.api_base

    tab_run, tab_eval, tab_metrics, tab_reports, tab_fusion, tab_use_cases = st.tabs(
        ["Scenarios", "Evaluate", "Metrics", "Reports", "Fusion", "Use Cases"]
    )

    with tab_run:
        # Carousel: one scenario card at a time with arrows
        assets_dir = Path(__file__).resolve().parents[1] / "assets"
        scenarios = [
            {"gif": "day.gif", "mp4": "data/samples/day.mp4", "name": "day.gif", "desc": "Day — Urban signage: Daylight urban, clear signs."},
            {"gif": "night.gif", "mp4": "data/samples/night.mp4", "name": "night.gif", "desc": "Night — Highway: Night highway, glare check."},
            {"gif": "rain.gif", "mp4": "data/samples/rain.mp4", "name": "rain.gif", "desc": "Rain — Adverse weather: Rainy road, low contrast."},
            {"gif": "tunnel.gif", "mp4": "data/samples/tunnel.mp4", "name": "tunnel.gif", "desc": "Tunnel — Lighting transition: Tunnel, bright→dark shift."},
            {"gif": "snow.gif", "mp4": "data/samples/snow.mp4", "name": "snow.gif", "desc": "Snow — Winter road: Snowy road, low contrast."},
            {"gif": "pedestrians.gif", "mp4": "data/samples/pedestrians.mp4", "name": "pedestrians.gif", "desc": "Pedestrians — Crosswalk: Busy crosswalk, pedestrians."},
        ]
        st.session_state.setdefault("scenario_idx", 0)
        st.session_state.setdefault("video_choice", scenarios[0]["mp4"])

        # Show three cards (Prev | Center | Next)
        n = len(scenarios)
        mid = int(st.session_state["scenario_idx"]) % n
        left_i = (mid - 1) % n
        right_i = (mid + 1) % n

        col_left, col_center, col_right = st.columns([1, 1, 1], gap="small")

        def render_card(col, idx, show_prev=False, show_next=False, show_select=False, highlight=False):
            item = scenarios[idx]
            gif_path = assets_dir / item["gif"]
            if not gif_path.exists():
                return
            import base64 as _b64
            b64 = _b64.b64encode(gif_path.read_bytes()).decode("utf-8")
            desc = item['desc']
            title, rest = desc.split(' — ', 1) if ' — ' in desc else (desc, '')
            sub, detail = rest.split(':', 1) if ':' in rest else (rest, '')
            with col:
                st.markdown(
                    f"""
                    <div class=\"{'gif-card highlight' if highlight else 'gif-card'}\">\
                      <div class=\"gif-title\">{title.strip()}</div>
                      <div class=\"gif-sub\">{sub.strip()}</div>
                      <div class=\"gif-desc\">{detail.strip()}</div>
                      <img src=\"data:image/gif;base64,{b64}\" />
                      <div class=\"gif-fn\">{item['name']}</div>
                    """,
                    unsafe_allow_html=True,
                )
                if show_prev and st.button("Prev.", key=f"prev_{idx}"):
                    st.session_state["scenario_idx"] = (mid - 1) % n
                    st.rerun()
                if show_select and st.button("Select", key=f"select_{idx}"):
                    st.session_state["video_choice"] = item["mp4"]
                    st.toast(f"Selected {item['mp4']}", icon="✅")
                if show_next and st.button("Next", key=f"next_{idx}"):
                    st.session_state["scenario_idx"] = (mid + 1) % n
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        # Outer frame
        st.markdown('<div class="carousel-frame">', unsafe_allow_html=True)
        row_l, row_c, row_r = st.columns([1,1,1], gap="small")
        render_card(row_l, left_i, show_prev=True)
        render_card(row_c, mid, show_select=True, highlight=True)
        render_card(row_r, right_i, show_next=True)
        st.markdown('</div>', unsafe_allow_html=True)

        with st.expander("Overlays & thresholds", expanded=True):
            ol1, ol2, ol3, ol4 = st.columns([1, 1, 1, 2])
            with ol1:
                show_boxes = st.checkbox("Boxes", value=True)
            with ol2:
                show_tracks = st.checkbox("Tracks", value=True)
            with ol3:
                show_ocr = st.checkbox("OCR", value=True)
            with ol4:
                profile = st.radio(
                    "",
                    options=["realtime", "accuracy"],
                    horizontal=True,
                    index=0,
                    label_visibility="collapsed",
                    key="profile_mode",
                )
            mask_opacity = st.slider("Mask opacity", 0.0, 1.0, 0.35, 0.05, help="Transparency of segmentation overlays")
            colt1, colt2 = st.columns(2)
            with colt1:
                conf_thresh = st.slider("Confidence", 0.05, 0.95, 0.35, 0.05)
            with colt2:
                nms_iou = st.slider("NMS IoU", 0.05, 0.95, 0.5, 0.05)
            class_filter = st.text_input("Class include (comma-separated)", value="", help="Limit overlays to these classes")

        st.markdown("### Telemetry")
        st.markdown('<div class="sticky-hud">', unsafe_allow_html=True)
        fps_placeholder = st.empty()
        hud_bar = st.empty()
        st.markdown('</div>', unsafe_allow_html=True)

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
                        t = ev.get("timings", {})
                        hud_bar.write(f"pre: {t.get('pre',0)} ms | model: {t.get('model',0)} ms | post: {t.get('post',0)} ms")
                    except Exception:
                        messages.append({"raw": msg})
                    # show only last few
                    log_box.json(messages[-5:])
            except Exception as e:
                log_box.warning(f"WS error: {e}")

        # Auto-start behavior removed per request to simplify controls

        st.markdown("---")
        st.subheader("Quick actions")
        colq1, colq2 = st.columns(2)
        with colq1:
            if st.button("Show last annotated frame"):
                try:
                    last = requests.get(f"{api_base}/last_event", timeout=8).json()
                    evt = last.get("event") or {}
                    meta_col, img_col = st.columns([1, 2])
                    with meta_col:
                        st.caption("Timings (ms)")
                        st.json(evt.get("timings", {}))
                        st.caption("Provider")
                        st.json(evt.get("provider_provenance", {}))
                    with img_col:
                        if evt.get("annotated_b64"):
                            st.image(evt["annotated_b64"], caption="Last annotated", use_column_width=True)
                        else:
                            st.info("No annotated image found.")
                except Exception as e:
                    st.warning(f"Failed to load last annotated frame: {e}")
        with colq2:
            if st.button("Interview Mode (2 min)"):
                try:
                    import time as _time
                    st.toast("Running realtime profile…", icon="▶️")
                    requests.post(f"{api_base}/run_video", json={"video_path": "data/samples/day.mp4", "profile": "realtime"}, timeout=10)
                    _time.sleep(5)
                    st.toast("Comparing profiles…", icon="🌓")
                    # Use the comparison block by triggering programmatically is tricky; show inline compare here
                    # Ask for one frame in both profiles and display side-by-side if image is uploaded later
                    st.info("Upload an image below to complete the realtime vs accuracy comparison.")
                    st.toast("Generating metrics…", icon="📈")
                    try:
                        requests.get(f"{api_base}/metrics", timeout=5)
                    except Exception:
                        pass
                    st.toast("Building PDF…", icon="📄")
                    last = requests.get(f"{api_base}/last_event", timeout=8).json()
                    rid = last.get("run_id")
                    if rid:
                        rep = requests.post(f"{api_base}/report", json={"run_id": rid}, timeout=30).json()
                        st.success(rep)
                        st.toast(f"Report saved to {rep.get('report_path')}", icon="✅")
                    else:
                        st.info("No recent run to report.")
                except Exception as e:
                    st.warning(f"Interview Mode encountered an issue: {e}")

        st.markdown("---")
        st.subheader("Single-frame detection test")
        uploaded = st.file_uploader("Upload image (jpg/png)", type=["jpg","jpeg","png"])
        with st.expander("Provider override (optional)"):
            det_provider = st.radio("Detection provider", ["default","replicate","hf","roboflow"], horizontal=True, index=0)
            det_model = st.text_input("Detector model/version (provider-specific)", value="ultralytics/yolov8")
            ocr_provider = st.radio("OCR provider", ["default","replicate","gcv","azure","textract"], horizontal=True, index=0)
            ocr_version = st.text_input("OCR version (Replicate PaddleOCR)", value="")
        if uploaded and st.button("Run /run_frame"):
            import base64
            img_b64 = base64.b64encode(uploaded.read()).decode("utf-8")
            try:
                with st.spinner("Running /run_frame..."):
                    override = None
                    if det_provider != "default":
                        override = {"detection": {"provider": det_provider, "model": det_model}}
                    if ocr_provider != "default":
                        override = override or {}
                        override.update({"ocr": {"provider": ocr_provider}})
                        if ocr_provider == "replicate" and ocr_version:
                            override["ocr"]["version"] = ocr_version
                    overlay_opts = {
                        "class_include": [c.strip() for c in class_filter.split(",") if c.strip()],
                        "mask_opacity": mask_opacity,
                        "conf_thresh": conf_thresh,
                        "nms_iou": nms_iou,
                        "show_boxes": show_boxes,
                        "show_tracks": show_tracks,
                        "show_ocr": show_ocr,
                    }
                    payload = {"image_b64": img_b64, "profile": profile, "provider_override": override, "overlay_opts": overlay_opts}
                    resp = requests.post(f"{api_base}/run_frame", json=payload, timeout=30)
                data = resp.json()
                col_a, col_b = st.columns(2)
                with col_a:
                    st.caption("Response JSON")
                    st.json(data)
                    if data.get("ocr"):
                        st.caption("OCR")
                        st.write(", ".join([o.get("text", "") for o in data.get("ocr", [])]))
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
                with st.spinner("Comparing profiles..."):
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
                    # Simple heatmap diff toggle
                    if st.checkbox("Show difference heatmap"):
                        import numpy as _np
                        import base64 as _b64
                        import cv2 as _cv
                        def _decode(b):
                            arr = _np.frombuffer(_b64.b64decode(b), dtype=_np.uint8)
                            return _cv.imdecode(arr, _cv.IMREAD_COLOR)
                        a = _decode(rt["annotated_b64"])
                        b = _decode(acc["annotated_b64"])
                        if a is not None and b is not None and a.shape == b.shape:
                            diff = _cv.absdiff(a, b)
                            heat = _cv.applyColorMap(_cv.cvtColor(_cv.cvtColor(diff, _cv.COLOR_BGR2GRAY), _cv.COLOR_GRAY2BGR), _cv.COLORMAP_JET)
                            ok, buf = _cv.imencode('.jpg', heat)
                            if ok:
                                st.image(_b64.b64encode(buf.tobytes()).decode('utf-8'), caption="Difference heatmap", use_column_width=True)
            except Exception as e:
                st.warning(f"Compare failed: {e}")

    with tab_eval:
        st.subheader("Evaluate")
        dataset = st.text_input("Dataset (COCO JSON)", value="data/labels/demo_annotations.json")
        tasks = st.multiselect("Tasks", options=["det","seg","track","ocr"], default=["det"]) 
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            if st.button("Run Eval"):
                try:
                    resp = requests.post(f"{api_base}/evaluate", json={"dataset": dataset, "tasks": tasks}, timeout=10)
                    st.json(resp.json())
                except Exception as e:
                    st.warning(f"API not reachable yet: {e}")
        with col_e2:
            if st.button("Load last metrics"):
                try:
                    m = requests.get(f"{api_base}/load_metrics", timeout=6).json()
                    st.json(m)
                except Exception as e:
                    st.warning(f"Failed to load metrics: {e}")

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
        st.markdown("---")
        st.subheader("Telemetry charts")
        if st.button("Load recent telemetry"):
            try:
                snap = requests.get(f"{api_base}/events_snapshot?limit=100", timeout=8).json()
                import pandas as _pd
                _df = _pd.DataFrame({
                    "frame": snap.get("frame_ids", []),
                    "fps": snap.get("fps", []),
                    "pre": snap.get("latency_pre", []),
                    "model": snap.get("latency_model", []),
                    "post": snap.get("latency_post", []),
                })
                if not _df.empty:
                    st.line_chart(_df.set_index("frame")["fps"], height=180)
                    st.area_chart(_df.set_index("frame")[["pre","model","post"]], height=220)
                else:
                    st.info("No telemetry yet.")
            except Exception as e:
                st.warning(f"Telemetry error: {e}")

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
                    # Download links
                    rid = last_run
                    col_d1, col_d2, col_d3 = st.columns(3)
                    with col_d1:
                        st.caption("Download logs")
                        st.code(f"runs/{rid}/events.jsonl")
                    with col_d2:
                        st.caption("Download metrics")
                        st.code(f"runs/{rid}/metrics.json")
                    with col_d3:
                        st.caption("Export run bundle")
                        try:
                            z = requests.post(f"{api_base}/export_run", json={"run_id": rid}, timeout=20).json()
                            st.code(z.get("zip_path"))
                        except Exception:
                            st.info("Bundle export unavailable.")
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

    with tab_use_cases:
        st.subheader("Use Cases")
        uc1, uc2, uc3, uc4, uc5 = st.tabs([
            "Roadway Traffic & Sign Intelligence",
            "Warehouse Safety & PPE",
            "Retail Shelf QA (OCR)",
            "Smart City Anomaly & Flow",
            "Agriculture Field Scan",
        ])

        def _decode_b64_to_cv(img_b64: str):
            import base64 as _b64, numpy as _np, cv2 as _cv
            arr = _np.frombuffer(_b64.b64decode(img_b64), dtype=_np.uint8)
            return _cv.imdecode(arr, _cv.IMREAD_COLOR)

        # 1) Roadway: focus on signs/lights + OCR list and compare heatmap
        with uc1:
            st.caption("Filter to traffic signs/lights, extract OCR, and compare profiles")
            up = st.file_uploader("Upload frame (jpg/png)", type=["jpg","jpeg","png"], key="uc1")
            if up and st.button("Analyze roadway frame", key="uc1btn"):
                import base64 as _b64
                img_b64 = _b64.b64encode(up.read()).decode("utf-8")
                try:
                    # Run realtime with class filters for signs/lights
                    payload = {
                        "image_b64": img_b64,
                        "profile": "realtime",
                        "overlay_opts": {"class_include": ["traffic-light","sign"], "mask_opacity": 0.35},
                    }
                    rt = requests.post(f"{api_base}/run_frame", json=payload, timeout=30).json()
                    st.image(rt.get("annotated_b64"), caption="Realtime (signs/lights)", use_column_width=True)
                    st.caption("OCR (if present)")
                    st.json(rt.get("ocr") or [])
                    # Compare to accuracy
                    acc = requests.post(f"{api_base}/run_frame", json={"image_b64": img_b64, "profile": "accuracy"}, timeout=30).json()
                    from streamlit_image_comparison import image_comparison
                    if rt.get("annotated_b64") and acc.get("annotated_b64"):
                        image_comparison(img1=rt["annotated_b64"], img2=acc["annotated_b64"], label1="Realtime", label2="Accuracy", width=700)
                except Exception as e:
                    st.warning(f"Error: {e}")

        # 2) Warehouse: virtual safety zones + person count inside
        with uc2:
            st.caption("Draw virtual safety zones and count people in-zone")
            up = st.file_uploader("Upload frame (jpg/png)", type=["jpg","jpeg","png"], key="uc2")
            x1 = st.number_input("Zone x1", 0, 2000, 100); y1 = st.number_input("Zone y1", 0, 2000, 100)
            x2 = st.number_input("Zone x2", 0, 2000, 600); y2 = st.number_input("Zone y2", 0, 2000, 400)
            if up and st.button("Check safety zones", key="uc2btn"):
                import base64 as _b64, cv2 as _cv
                img_b64 = _b64.b64encode(up.read()).decode("utf-8")
                try:
                    rt = requests.post(f"{api_base}/run_frame", json={"image_b64": img_b64, "profile": "realtime"}, timeout=30).json()
                    im = _decode_b64_to_cv(rt.get("annotated_b64"))
                    if im is not None:
                        _cv.rectangle(im, (int(x1), int(y1)), (int(x2), int(y2)), (0,0,255), 2)
                        # Count persons in zone
                        cnt = 0
                        for b in rt.get("boxes", []):
                            if b.get("cls") == "person":
                                bx1, by1, bx2, by2 = b["x1"], b["y1"], b["x2"], b["y2"]
                                if bx1 < x2 and bx2 > x1 and by1 < y2 and by2 > y1:
                                    cnt += 1
                        st.metric("People in zone", cnt)
                        ok, buf = _cv.imencode('.jpg', im)
                        if ok:
                            import base64 as _b64
                            st.image(_b64.b64encode(buf.tobytes()).decode('utf-8'), use_column_width=True)
                except Exception as e:
                    st.warning(f"Error: {e}")

        # 3) Retail shelf: OCR table and download CSV
        with uc3:
            st.caption("Extract price/label text and review as a table")
            up = st.file_uploader("Upload frame (jpg/png)", type=["jpg","jpeg","png"], key="uc3")
            if up and st.button("Extract OCR", key="uc3btn"):
                import base64 as _b64, pandas as _pd
                img_b64 = _b64.b64encode(up.read()).decode("utf-8")
                try:
                    rt = requests.post(f"{api_base}/run_frame", json={"image_b64": img_b64, "profile": "accuracy"}, timeout=30).json()
                    ocr = rt.get("ocr") or []
                    if ocr:
                        df = _pd.DataFrame(ocr)
                        st.dataframe(df, use_container_width=True)
                        st.download_button("Download CSV", df.to_csv(index=False).encode("utf-8"), "ocr.csv", "text/csv")
                    else:
                        st.info("No OCR items returned.")
                except Exception as e:
                    st.warning(f"Error: {e}")

        # 4) Smart city: flow strip charts and anomaly hint
        with uc4:
            st.caption("Visualize flow and latency; flag anomalies")
            if st.button("Load recent telemetry", key="uc4btn"):
                try:
                    snap = requests.get(f"{api_base}/events_snapshot?limit=120", timeout=8).json()
                    import pandas as _pd
                    _df = _pd.DataFrame({
                        "frame": snap.get("frame_ids", []),
                        "fps": snap.get("fps", []),
                        "pre": snap.get("latency_pre", []),
                        "model": snap.get("latency_model", []),
                        "post": snap.get("latency_post", []),
                    })
                    if not _df.empty:
                        st.line_chart(_df.set_index("frame")["fps"], height=180)
                        st.area_chart(_df.set_index("frame")[["pre","model","post"]], height=220)
                        st.caption("Anomaly hint: spikes above 3× median are flagged")
                        med = float(_df[["pre","model","post"]].median().sum())
                        spikes = _df[( _df[["pre","model","post"]].sum(axis=1) > 3*med )]["frame"].tolist()
                        st.write({"spike_frames": spikes[:10]})
                    else:
                        st.info("No telemetry yet.")
                except Exception as e:
                    st.warning(f"Error: {e}")

        # 5) Agriculture: simple green mask and obstacle highlight
        with uc5:
            st.caption("Approximate vegetation mask and highlight obstacles")
            up = st.file_uploader("Upload frame (jpg/png)", type=["jpg","jpeg","png"], key="uc5")
            if up and st.button("Analyze field", key="uc5btn"):
                import numpy as _np, cv2 as _cv
                import base64 as _b64
                img_b64 = _b64.b64encode(up.read()).decode("utf-8")
                try:
                    rt = requests.post(f"{api_base}/run_frame", json={"image_b64": img_b64, "profile": "realtime"}, timeout=30).json()
                    im = _decode_b64_to_cv(rt.get("annotated_b64"))
                    if im is not None:
                        hsv = _cv.cvtColor(im, _cv.COLOR_BGR2HSV)
                        lower = _np.array([35, 40, 40]); upper = _np.array([85, 255, 255])
                        mask = _cv.inRange(hsv, lower, upper)
                        veg = _cv.applyColorMap(_cv.cvtColor(mask, _cv.COLOR_GRAY2BGR), _cv.COLORMAP_SUMMER)
                        overlay = _cv.addWeighted(im, 0.7, veg, 0.3, 0)
                        ok, buf = _cv.imencode('.jpg', overlay)
                        if ok:
                            st.image(_b64.b64encode(buf.tobytes()).decode('utf-8'), use_column_width=True)
                except Exception as e:
                    st.warning(f"Error: {e}")


if __name__ == "__main__":
    main()


