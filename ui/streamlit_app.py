from __future__ import annotations

import time
from pathlib import Path
import os
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))

import streamlit as st
import requests
import threading
import json as _json
from urllib.parse import urlencode
from app.services.client import HttpClient
from app.services.offline_client import OfflineClient


def get_logo_path() -> Path:
    # Resolve path to assets/pl-ani.gif relative to this file
    return Path(__file__).resolve().parents[1] / "assets" / "pl-ani.gif"

def get_splash_logo_path() -> Path:
    # Prefer pl-loop.gif for splash if present, else fall back to pl-ani.gif
    assets = Path(__file__).resolve().parents[1] / "assets"
    loop = assets / "pl-loop.gif"
    return loop if loop.exists() else assets / "pl-ani.gif"


def inject_base_styles() -> None:
    st.markdown(
        """
        <style>
        :root { --cardw: 310px; --aqua:#02ABC1; }
        /* App background */
        .stApp { background-color: #060F25; }
        /* Global font family */
        html, body, .stApp, [class^="css"], [class*=" css"], .stMarkdown, .stText, .stButton, .stTabs {
            font-family: 'Century Gothic', CenturyGothic, AppleGothic, 'Segoe UI', 'Inter', system-ui, -apple-system, sans-serif !important;
        }
        /* Remove default top gaps so banner is flush */
        [data-testid="stHeader"] { display: none; }
        .block-container { padding-top: 0 !important; padding-bottom: 0 !important; }
        .block-container > div:first-child { margin-top: 0 !important; }
        .block-container > div:last-child { margin-bottom: 0 !important; }
        .stMain { padding-top: 0 !important; padding-bottom: 0 !important; }

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
        .top-banner img { max-height: 173px; display: block; margin: 0; }
        .stButton>button { transition: all 200ms ease-in-out; border-radius: 8px; }
        .stButton>button { white-space: nowrap; }
        .card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); padding: 12px 14px; border-radius: 12px; box-shadow: 0 6px 18px rgba(0,0,0,0.18); }
        .sticky-right { position: sticky; top: 90px; }
        #preview-pane { position: sticky; top: 90px; }
        .sticky-hud { position: sticky; top: 6px; z-index: 100; background: rgba(6,15,37,0.85); backdrop-filter: blur(4px); padding: 6px 10px; border-radius: 8px; border: 1px solid rgba(2,171,193,0.2); }

        /* Centering helpers */
        .center { display: flex; align-items: center; justify-content: center; }

        /* Hotkeys hint */
        .hotkeys { color: #8fbac0; font-size: 12px; }

        /* Tabs: larger, distinct, high-contrast */
        .stTabs { margin-top: 0 !important; margin-bottom: 0 !important; }
        .stTabs [data-baseweb="tab-list"] { margin: 0 !important; }
        .stTabs + div { margin-top: 0 !important; }
        .stTabs [data-baseweb="tab-list"] {
            display: flex;
            gap: 14px;
            justify-content: space-between;
            border-bottom: 1px solid rgba(255,255,255,0.08);
            padding-bottom: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            font-family: 'Century Gothic', CenturyGothic, AppleGothic, 'Segoe UI', 'Inter', system-ui, -apple-system, sans-serif;
            font-weight: 700 !important;
            font-size: 1.5rem !important;
            letter-spacing: 0.015em;
            color: var(--aqua); /* default: blue-green */
            padding: 18px 24px;
            border-radius: 14px 14px 0 0;
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.10);
            box-shadow: 0 2px 4px rgba(0,0,0,0.15) inset;
            transition: all 160ms ease-in-out;
            flex: 1 1 0;
            text-align: center;
            min-width: 0;
        }
        .stTabs [data-baseweb="tab"] * { font-size: inherit !important; font-weight: inherit !important; line-height: 1.25 !important; }
        .stTabs [data-baseweb="tab"]:hover {
            color: #e6fbfe;
            background: rgba(2,171,193,0.12);
            border-color: rgba(2,171,193,0.35);
        }
        .stTabs [aria-selected="true"] {
            color: #ffffff !important; /* selected: white */
            background: linear-gradient(180deg, rgba(2,171,193,0.20), rgba(2,171,193,0.05));
            border-color: rgba(2,171,193,0.45);
            box-shadow: 0 0 0 1px rgba(2,171,193,0.28), 0 8px 18px rgba(2,171,193,0.14);
            font-weight: 800 !important;
            text-shadow: 0 0 6px rgba(2,171,193,0.25);
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
            width: var(--cardw); /* fixed card width */
            box-sizing: border-box; /* include border in width to avoid overflow */
            margin: 0; /* prevent extra spacing that causes 4th card bleed */
        }
        .gif-card img { display: block; width: 100%; height: auto; object-fit: contain; }
        .gif-card .gif-cap { color: #cfeaf0; font-size: 12px; margin-top: 8px; }
        .gif-card .gif-title { color: #e6fbfe; font-size: 1.15rem; font-weight: 800; text-align: center; }
        .gif-card .gif-sub { color: #cfeaf0; font-size: 1.0rem; font-weight: 700; text-align: center; }
        .gif-card .gif-desc { color: #9fc7ce; font-size: 0.95rem; margin-top: 2px; text-align: center; }
        .gif-card .gif-fn { color: #9fc7ce; font-size: 0.85rem; margin-top: 8px; word-break: break-all; text-align: center; }
        /* Use Streamlit form as a reliable wrapper for the trio so the border encloses cards + buttons */
        [data-testid="stForm"] {
            border: 1px solid #ffffff;
            border-radius: 10px;
            padding: 4px 10px; /* very tight vertical padding */
            margin: 0 auto;  /* tighter outer spacing */
            background: rgba(255,255,255,0.02);
            text-align: center;
        }
        .carousel-center { display:flex; width:100%; text-align:center; }
        .carousel-frame { display:inline-block; margin: 0 auto; padding: 0; }
        .carousel-viewport { width: calc(3 * var(--cardw)); overflow: hidden; margin: 0 auto; padding: 0; }
        .carousel-track { display: flex; gap: 0; will-change: transform; justify-content: center; }
        .slide-next { transform: translateX(0); animation: slideNext 280ms ease-out forwards; }
        .slide-prev { transform: translateX(calc(-3 * var(--cardw))); animation: slidePrev 280ms ease-out forwards; }
        @keyframes slideNext {
            from { transform: translateX(0); }
            to { transform: translateX(calc(-3 * var(--cardw))); }
        }
        @keyframes slidePrev {
            from { transform: translateX(calc(-3 * var(--cardw))); }
            to { transform: translateX(0); }
        }
        .carousel-row { display: flex; gap: 12px; justify-content: center; align-items: stretch; }

        /* Button row: make form buttons large, adjacent, centered under center card */
        [data-testid="stForm"] .stButton { display: inline-block; margin: 0; }
        [data-testid="stForm"] .stButton > button {
            width: calc(var(--cardw)/3);
            height: 44px;
            font-size: 22px;
            font-weight: 700;
            border-radius: 0;
        }
        /* Remove seams between adjacent buttons */
        [data-testid="stForm"] .stButton + .stButton > button { margin-left: -1px; }
        /* Emphasize the middle (Select) button */
        [data-testid="stForm"] .stButton:nth-of-type(2) > button {
            border: 3px solid #ffffff !important;
            background: rgba(255,255,255,0.06);
        }
        .gif-card.highlight { border: 3px solid #ffffff; box-shadow: 0 0 0 2px rgba(255,255,255,0.12) inset; }
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
            width: 100vw; /* fill available screen width */
            max-width: 100%;
            opacity: 0.85;
            /* Stronger, deeper fade with emphasis on top/bottom */
            -webkit-mask-image: radial-gradient(ellipse at 50% 50%, rgba(0,0,0,1) 24%, rgba(0,0,0,0.35) 55%, rgba(0,0,0,0.12) 78%, rgba(0,0,0,0) 100%);
                    mask-image: radial-gradient(ellipse at 50% 50%, rgba(0,0,0,1) 24%, rgba(0,0,0,0.35) 55%, rgba(0,0,0,0.12) 78%, rgba(0,0,0,0) 100%);
        }
        .banner-logo {
            max-height: 173px; /* ~90% of previous */
            opacity: 0.85;
            -webkit-mask-image: radial-gradient(circle at 50% 50%, rgba(0,0,0,1) 50%, rgba(0,0,0,0.45) 75%, rgba(0,0,0,0.18) 90%, rgba(0,0,0,0) 100%);
                    mask-image: radial-gradient(circle at 50% 50%, rgba(0,0,0,1) 50%, rgba(0,0,0,0.45) 75%, rgba(0,0,0,0.18) 90%, rgba(0,0,0,0) 100%);
        }
        .sticky-right {
            position: sticky;
            top: 100px; /* Adjust based on header height */
            right: 0;
            width: 300px; /* Fixed width for the right panel */
            padding: 10px;
            background-color: #060F25;
            border-radius: 8px;
            box-shadow: -5px 0 10px rgba(0,0,0,0.3);
            z-index: 10;
        }
        /* Stepper */
        .stepper { display:flex; gap:8px; align-items:center; margin: 6px 0 2px 0; }
        .step { padding: 4px 10px; border-radius: 999px; border: 1px solid rgba(255,255,255,0.14); font-size: 12px; color:#cfeaf0; background: rgba(255,255,255,0.04); }
        .step.active { color: #01232a; background: var(--aqua); border-color: rgba(2,171,193,0.65); font-weight: 700; }
        .step.disabled { opacity: 0.45; filter: grayscale(0.5); }
        .stepper-hint { font-size: 12px; color:#9fc7ce; margin-bottom: 6px; }
        /* Focus outlines for accessibility */
        .stButton>button:focus-visible { outline: 2px solid #02ABC1 !important; box-shadow: 0 0 0 3px rgba(2,171,193,0.35) !important; }
        /* Simple skeletons */
        .skeleton { width:100%; height:160px; border-radius:8px; background: linear-gradient(90deg, rgba(255,255,255,0.06), rgba(255,255,255,0.12), rgba(255,255,255,0.06)); background-size: 600% 100%; animation: shine 1.2s infinite; }
        @keyframes shine { 0% { background-position: 0% 0; } 100% { background-position: 100% 0; } }
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
            <div style="position:fixed; inset:0; background-color:#060F25; padding:0; margin:0; width:100vw; height:100vh; overflow:hidden; z-index: 9999;">
              <img class="splash-logo" src="{img_src}" alt="PerceptionLab" style="display:block; width:100%; height:auto; margin:0;"/>
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
            r = requests.get(f"{base}/health", timeout=0.2)
            return r.ok
        except Exception:
            return False

    logo_path = get_logo_path()
    if not st.session_state.get("splash_done", False):
        show_splash(get_splash_logo_path())
        st.session_state["splash_done"] = True
        st.rerun()

    render_top_banner(logo_path)

    # Offline mode detection
    offline_env = os.getenv("PERCEPTION_OFFLINE", "").strip()
    offline = offline_env not in ("", "0", "false", "False")
    _ok = _ping_api(st.session_state.api_base)
    if offline or not _ok:
        st.session_state.offline = True
        _ok = True  # treat as connected for UX
    else:
        st.session_state.offline = False
    _badge = "🟢 Connected" if _ok else "🔴 Offline"
    # Providers readiness badge
    prov_ok = False
    try:
        pr = requests.get(f"{st.session_state.api_base}/health/providers", timeout=1.5)
        if pr.ok:
            prov = (pr.json() or {}).get("providers", {})
            prov_ok = bool(prov) and all(bool(v) for v in prov.values())
    except Exception:
        prov_ok = False
    _prov_badge = "🟢 Providers" if prov_ok else "🟠 Providers"
    st.markdown(
        f"""
        <div style=\"position:fixed; top:8px; right:12px; z-index:1000; font-size:12px; opacity:.95; background:rgba(6,14,38,0.6); padding:4px 8px; border-radius:8px; border:1px solid rgba(255,255,255,0.15);\">\n          <span>{_badge}</span>\n        </div>\n        <div style=\"position:fixed; top:34px; right:12px; z-index:1000; font-size:12px; opacity:.95; background:rgba(6,14,38,0.6); padding:4px 8px; border-radius:8px; border:1px solid rgba(255,255,255,0.15);\">\n          <span title=\"Provider tokens/endpoints configured\">{_prov_badge}</span>\n        </div>
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

    tab_run, tab_eval, tab_monitor, tab_fusion = st.tabs(
        ["Detect", "Evaluate", "Monitor", "Fusion"]
    )

    # Initialize client
    client = OfflineClient() if st.session_state.get("offline") else HttpClient(st.session_state.api_base)

    with tab_run:
        # Scenarios: Gallery → Focus flow
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
        st.session_state.setdefault("view_mode", "gallery")  # gallery | focus
        st.session_state.setdefault("selected_scenario", None)

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

        if st.session_state.view_mode == "gallery":
            # Single bordered wrapper using a simple container + HTML frame
            with st.container():
                import base64 as _b64
                def _card_html(idx: int, highlight: bool) -> str:
                    item = scenarios[idx]
                    gif_path = assets_dir / item["gif"]
                    if not gif_path.exists():
                        return ""
                    b64 = _b64.b64encode(gif_path.read_bytes()).decode("utf-8")
                    desc_text = str(item.get('desc', ''))
                    if ' — ' in desc_text:
                        title, rest = desc_text.split(' — ', 1)
                    else:
                        title, rest = desc_text, ''
                    if ':' in rest:
                        sub, detail = rest.split(':', 1)
                    else:
                        sub, detail = rest, ''
                    label_fn = Path(item.get("mp4", "")).name or ""
                    card_cls = "gif-card highlight" if highlight else "gif-card"
                    return (
                        f"<div class='{card_cls}' style='margin:0;'>"
                        f"  <div class='gif-title'>{title.strip()}</div>"
                        f"  <div class='gif-sub'>{sub.strip()}</div>"
                        f"  <div class='gif-desc'>{detail.strip()}</div>"
                        f"  <img src='data:image/gif;base64,{b64}' />"
                        f"  <div class='gif-fn'>{label_fn}</div>"
                        f"</div>"
                    )

                # Build exactly three cards: left, center (highlight), right
                track_class = "carousel-track"
                track_style = ""
                track_html = (
                    _card_html(left_i, False)
                    + _card_html(mid, True)
                    + _card_html(right_i, False)
                )

                # Center block via Streamlit columns
                st.markdown("<div class='carousel-center'><div class='carousel-frame'>", unsafe_allow_html=True)
                st.markdown(
                    f"<div class='carousel-viewport'><div class='{track_class}' style='{track_style}'>{track_html}</div></div>",
                    unsafe_allow_html=True,
                )
                # Buttons row with wider spacers to avoid wrapping
                sp1, cbl, cbs, cbr, sp2 = st.columns([3,1,1,1,3])
                prev_clicked = cbl.button("< PREV", use_container_width=True)
                select_clicked = cbs.button("SELECT", use_container_width=True)
                next_clicked = cbr.button("NEXT >", use_container_width=True)
                st.markdown("</div></div>", unsafe_allow_html=True)

            if prev_clicked:
                st.session_state["scenario_idx"] = (mid - 1) % n
                st.rerun()
            if select_clicked:
                st.session_state["video_choice"] = scenarios[mid]["mp4"]
                st.session_state["selected_scenario"] = scenarios[mid]
                st.session_state["view_mode"] = "focus"
                st.rerun()
            if next_clicked:
                st.session_state["scenario_idx"] = (mid + 1) % n
                st.rerun()

            # No animation flags; stable 3-card render

            # Stop further rendering in gallery mode to prevent stray sections
            st.stop()

        else:
            # Focus mode: selected preview on the right, tools on the left
            sel = st.session_state.get("selected_scenario")
            # Ensure state flags
            st.session_state.setdefault("is_running", False)
            st.session_state.setdefault("has_run", False)
            st.session_state.setdefault("show_ab", False)
            # Artifacts flag
            runs_dir = Path("runs/latest")
            has_artifacts = False
            if runs_dir.exists():
                for p in runs_dir.iterdir():
                    if p.is_file():
                        has_artifacts = True
                        break
            st.session_state["has_artifacts"] = has_artifacts
            # Determine current step (1..4): 1(select) -> 2(run) -> 3(compare) -> 4(export)
            ab_comp = (runs_dir/"ab_composite.png").exists() if runs_dir.exists() else False
            report_exists = (runs_dir/"report.pdf").exists() if runs_dir.exists() else False
            curr_step = 1
            if st.session_state.get("has_run"): curr_step = 2
            if st.session_state.get("show_ab"): curr_step = 3
            if report_exists or ab_comp: curr_step = 4
            left, right = st.columns([7,5])
            rendered_side_panels = False
            # Scenario source path availability for both columns
            mp4 = (sel or {}).get("mp4")
            mp4_ok = bool(mp4 and Path(mp4).exists())

            # Header (full-width above columns)
            name_text = (sel or {}).get("desc", "")
            hdr_left, hdr_right = st.columns([8,4])
            with hdr_left:
                # Scenario workspace heading moved below preview in right column per layout request
                st.markdown("")
            with hdr_right:
                pass
            # Left column content begins
            with left:
                st.markdown("")

            with right:
                try:
                    import base64 as _b64
                    gif_b64 = _b64.b64encode((assets_dir / sel["gif"]).read_bytes()).decode("utf-8") if sel else ""
                except Exception:
                    gif_b64 = ""
                # Sticky preview panel
                st.markdown("<div id='preview-pane' class='sticky-right card'>", unsafe_allow_html=True)
                if gif_b64:
                    alt = f"Scenario preview: {name_text}"
                    st.markdown(
                        f"<img src='data:image/gif;base64,{gif_b64}' alt='{alt}' style='width:100%;height:auto;border-radius:8px' />",
                        unsafe_allow_html=True,
                    )
                # Back arrow button (bottom-right under preview)
                _sp1, _sp2 = st.columns([10,1])
                with _sp2:
                    if st.button("⟵", key="back_to_gallery_right", help="Back to gallery"):
                        st.session_state.update(
                            view_mode="gallery",
                            selected_scenario=None,
                            show_ab=False,
                            has_run=False,
                            has_artifacts=False,
                            is_running=False,
                            carousel_anim="",
                        )
                        st.rerun()
                
                # Scenario metadata (lighting/env/features)
                _sname = (sel or {}).get("mp4", "")
                _stem = Path(_sname).stem if _sname else ""
                META = {
                    "day": "lighting: day | env: urban | features: signage",
                    "night": "lighting: night | env: highway | features: glare",
                    "rain": "weather: rain | env: roadway | features: low contrast",
                    "tunnel": "lighting: transition | env: tunnel | features: bright→dark",
                    "pedestrians": "env: crosswalk | features: pedestrians",
                    "snow": "weather: snow | env: roadway | features: low contrast",
                }
                meta = sel.get("meta", META.get(_stem, ""))
                if name_text:
                    st.caption(name_text)
                if meta:
                    st.caption(meta)
                # Small HUD (toggled in overlays on left)
                if st.session_state.get("show_hud", False):
                    hud_vals = st.session_state.get("hud_vals", {"fps":"—","pre":"—","model":"—","post":"—"})
                    st.markdown(
                        f"""
                        <div style='text-align:right; font-size:12px; opacity:0.85;'>
                          FPS {hud_vals.get('fps','—')} — pre {hud_vals.get('pre','—')} ms | model {hud_vals.get('model','—')} ms | post {hud_vals.get('post','—')} ms
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                # Buttons under preview
                btnc1, btnc2 = st.columns([1,1])
                with btnc1:
                    if mp4_ok and st.button("Open Video", use_container_width=True, help="Open the original input video"):
                        mp4 = (sel or {}).get("mp4")
                        if mp4 and Path(mp4).exists():
                            st.success(f"Source: {mp4}")
                        else:
                            st.warning("MP4 missing.")
                with btnc2:
                    # Copy path via Clipboard API (escape braces in f-string)
                    import json as _json
                    mp4 = (sel or {}).get("mp4") or ""
                    _mp4_js = _json.dumps(mp4)
                    st.markdown(
                        f"""
                        <button id='copy-path-btn' style='width:100%;padding:6px 10px;border-radius:8px;border:1px solid rgba(255,255,255,0.25);background:rgba(255,255,255,0.06);color:#cfeaf0;'>Copy path</button>
                        <script>
                        (function(){{
                          const b=document.getElementById('copy-path-btn');
                          if(b){{ b.onclick=async()=>{{ try{{ await navigator.clipboard.writeText({_mp4_js}); }}catch(e){{ console.log(e); }} }} }}
                        }})();
                        </script>
                        """,
                        unsafe_allow_html=True,
                    )
                st.markdown("</div>", unsafe_allow_html=True)
                # Move Artifacts and Bookmarks under the preview on the right
                from pathlib import Path as _P
                st.markdown("### Artifacts")
                # Prefer data/offline last_frame if present in offline mode
                last_frame = _P("runs/latest/last_frame.png")
                if st.session_state.get("offline") and _P("data/offline/last_frame.png").exists():
                    last_frame = _P("data/offline/last_frame.png")
                ab_comp = _P("runs/latest/ab_composite.png")
                out_mp4 = _P("runs/latest/out.mp4")
                report_pdf = _P("runs/latest/report.pdf")
                rac1, rac2 = st.columns([1,1])
                if has_artifacts:
                    with rac1:
                        if last_frame.exists():
                            st.image(str(last_frame), caption="last_frame.png", use_column_width=True)
                            if st.button("Copy path (image)"):
                                st.info(str(last_frame))
                        if ab_comp.exists():
                            st.image(str(ab_comp), caption="ab_composite.png", use_column_width=True)
                            if st.button("Copy path (composite)"):
                                st.info(str(ab_comp))
                    with rac2:
                        if out_mp4.exists():
                            st.video(str(out_mp4))
                            if st.button("Copy path (video)"):
                                st.info(str(out_mp4))
                        if report_pdf.exists():
                            st.link_button("Open report (PDF)", report_pdf.as_posix(), use_container_width=True)
                            if st.button("Copy path (report)"):
                                st.info(str(report_pdf))
                    st.caption("Artifacts reflect the current mode and overlay settings at capture time.")
                else:
                    if st.session_state.get("is_running"):
                        st.markdown("<div class='skeleton'></div>", unsafe_allow_html=True)
                    else:
                        st.caption("Artifacts appear here after a run or compare.")

                # Bookmarks in right column
                if st.button("Bookmark frame", key="__bookmark_btn__"):
                    try:
                        import json as _json
                        rows = st.session_state.get("telemetry_rows", [])
                        fid = rows[-1].get("frame_id") if rows else None
                        bk = {"ts": time.time(), "frame_id": fid, "scenario": (sel or {}).get("mp4")}
                        p = _P("runs/latest/bookmarks.json")
                        arr = []
                        if p.exists():
                            arr = _json.loads(p.read_text(encoding="utf-8"))
                        arr.append(bk)
                        p.write_text(_json.dumps(arr, indent=2), encoding="utf-8")
                        st.toast("Bookmarked.", icon="🔖")
                    except Exception as e:
                        st.warning(f"Bookmark failed: {e}")
                try:
                    import json as _json
                    bp = _P("runs/latest/bookmarks.json")
                    if bp.exists():
                        st.markdown("#### Bookmarks")
                        arr = _json.loads(bp.read_text(encoding="utf-8"))
                        for bmk in arr[-5:][::-1]:
                            cols = st.columns([3,1,1])
                            with cols[0]:
                                st.caption(f"Frame {bmk.get('frame_id')} — {Path((bmk.get('scenario') or '')).name}")
                            with cols[1]:
                                if st.button("Open frame", key=f"bk_open_{bmk.get('ts')}"):
                                    try:
                                        lf = _P("runs/latest/last_frame.png")
                                        if lf.exists():
                                            st.image(str(lf), caption="Last frame")
                                        else:
                                            st.info("No last_frame.png yet.")
                                    except Exception as _e:
                                        st.warning(f"Open failed: {_e}")
                            with cols[2]:
                                if st.button("Copy", key=f"bk_copy_{bmk.get('ts')}"):
                                    st.info(str(bp))
                except Exception:
                    pass
                rendered_side_panels = True
                # Scenario workspace info under right column content
                st.markdown("#### Scenario workspace")
                if name_text:
                    st.caption(name_text)
                st.caption("Pick mode, run a short segment, compare, and export artifacts.")

            with left:
                # Stepbar: labels outside, bigger text inside buttons
                st.markdown(
                    """
                    <div style='display:flex;gap:14px;align-items:center;flex-wrap:wrap;'>
                      <div style='display:flex;gap:8px;align-items:center;'>
                        <span style='opacity:.85;font-size:14px;font-weight:400;'>STEP 1:</span>
                        <button style='font-size:13px;font-weight:700;padding:5px 10px;border:1px solid rgba(255,255,255,0.25);border-radius:8px;background:rgba(255,255,255,0.06);color:#cfeaf0;'>SELECT</button>
                      </div>
                      <div style='display:flex;gap:8px;align-items:center;'>
                        <span style='opacity:.85;font-size:14px;font-weight:400;'>STEP 2:</span>
                        <button style='font-size:13px;font-weight:700;padding:5px 10px;border:1px solid rgba(255,255,255,0.25);border-radius:8px;background:rgba(255,255,255,0.06);color:#cfeaf0;'>RUN</button>
                      </div>
                      <div style='display:flex;gap:8px;align-items:center;'>
                        <span style='opacity:.85;font-size:14px;font-weight:400;'>STEP 3:</span>
                        <button style='font-size:13px;font-weight:700;padding:5px 10px;border:1px solid rgba(255,255,255,0.25);border-radius:8px;background:rgba(255,255,255,0.06);color:#cfeaf0;'>COMPARE</button>
                      </div>
                      <div style='display:flex;gap:8px;align-items:center;'>
                        <span style='opacity:.85;font-size:14px;font-weight:400;'>STEP 4:</span>
                        <button style='font-size:13px;font-weight:700;padding:5px 10px;border:1px solid rgba(255,255,255,0.25);border-radius:8px;background:rgba(255,255,255,0.06);color:#cfeaf0;'>EXPORT</button>
                      </div>
                    </div>
                    <div class='stepper-hint' style='margin-top:6px;'>Follow steps left to right.</div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

                # Mode selector + microcopy (hint to the right of the radio)
                col_r, col_hint = st.columns([1, 2])
                with col_r:
                    profile = st.radio(
                        "",
                        options=["realtime", "accuracy"],
                        horizontal=True,
                        index=0,
                        label_visibility="collapsed",
                        key="profile_mode_focus",
                    )
                with col_hint:
                    st.markdown("<span style='font-size:12px; opacity:.85'>(Realtime prioritizes throughput. Accuracy prioritizes detail.)</span>", unsafe_allow_html=True)
                # Make radio labels smaller and all-caps via CSS
                st.markdown(
                    """
                    <style>
                    /* target immediate radio labels in this block */
                    div[role='radiogroup'] label p { text-transform: uppercase; font-size: 12px; }
                    </style>
                    """,
                    unsafe_allow_html=True,
                )
                # Profile badges (compact, with tooltips)
                _inp = 640 if profile == "realtime" else 1024
                _conf = float(st.session_state.get("conf_thresh_focus", 0.35))
                _nms = float(st.session_state.get("nms_iou_focus", 0.5))
                st.markdown(
                    f"""
                    <div style='display:flex;gap:12px;align-items:center;margin:6px 0 0 0;'>
                      <span title='Input size sent to the perception models' style='font-size:12px;opacity:.9;'>Input {_inp}</span>
                      <span title='Minimum detection confidence retained' style='font-size:12px;opacity:.9;'>Conf ≥ {(_conf):.2f}</span>
                      <span title='IoU threshold used to merge overlapping boxes' style='font-size:12px;opacity:.9;'>NMS IoU {(_nms):.2f}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                # Advanced details
                with st.expander("Profile details (advanced)", expanded=False):
                    st.markdown("- Input size: {}px".format(_inp))
                    st.markdown("- Confidence threshold: {:.2f}".format(_conf))
                    st.markdown("- NMS IoU: {:.2f}".format(_nms))
                    _view_raw = st.checkbox("View raw", value=False, key="view_raw_profile_json")
                    if _view_raw:
                        import json as _json
                        st.code(_json.dumps({"input_size": _inp, "confidence_thresh": _conf, "nms_iou": _nms}, indent=2), language="json")
                st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

                # Primary actions row
                a1, a2, a3, a4 = st.columns([1.0,2.0,1.0,1.6])
                running = st.session_state.get("_run10s_running", False)
                mp4 = (sel or {}).get("mp4")
                mp4_ok = bool(mp4 and Path(mp4).exists())
                disabled_common = running or (not _ok) or (not mp4_ok)
                with a1:
                    if st.button("Run 10s", type="primary", use_container_width=True, disabled=disabled_common, help="Process a short segment with current mode and settings"):
                        if mp4_ok:
                            st.session_state["_run10s_running"] = True
                            st.session_state["has_run"] = True
                            st.toast("Processing 10 seconds…", icon="▶️")
                            try:
                                # Build overlays and thresholds payload from UI state
                                overlays = {
                                    "boxes": st.session_state.get("ov_boxes_focus", True),
                                    "tracks": st.session_state.get("ov_tracks_focus", True),
                                    "ocr": st.session_state.get("ov_ocr_focus", True),
                                    "hud": st.session_state.get("ov_hud_focus", False),
                                }
                                thresholds = {
                                    "confidence": st.session_state.get("conf_thresh_focus", 0.35),
                                    "nms_iou": st.session_state.get("nms_iou_focus", 0.5),
                                    "mask_opacity": st.session_state.get("mask_opacity_focus", 0.35),
                                    "include": st.session_state.get("class_filter_focus", ""),
                                }
                                # Persist a small profile snapshot alongside artifacts for reporting/audit
                                try:
                                    from pathlib import Path as _P
                                    import json as _json
                                    _snap = {
                                        "profile": profile,
                                        "input_size": _inp,
                                        "thresholds": thresholds,
                                    }
                                    _P("runs/latest").mkdir(parents=True, exist_ok=True)
                                    (_P("runs/latest")/"profile.json").write_text(_json.dumps(_snap, indent=2), encoding="utf-8")
                                except Exception:
                                    pass
                                client.run_video(mp4, profile, duration_s=10, emit_video=False, overlays=overlays, thresholds=thresholds)
                                st.toast("Finished.", icon="✅")
                            except Exception as e:
                                st.warning(f"Run failed: {e}")
                            st.session_state["_run10s_running"] = False
                        else:
                            st.warning("Missing MP4; actions disabled.")
                with a2:
                    disabled_compare = running or (not _ok) or (not mp4_ok)
                    if st.button("Compare profiles (A/B)", help="Capture the same frame in both profiles and open a slider", use_container_width=True, disabled=disabled_compare):
                        import shutil as _sh
                        from pathlib import Path as _P
                        st.toast("Preparing A/B images…", icon="🌓")
                        did_ab = False
                        # If offline, prefer local fallback directly (data/offline first)
                        if st.session_state.get("offline"):
                            off = _P("data/offline")
                            dst = _P("runs/latest"); dst.mkdir(parents=True, exist_ok=True)
                            left = off/"realtime_frame.png"; right = off/"accuracy_frame.png"
                            if left.exists() and right.exists():
                                _sh.copyfile(str(left), str(dst/"realtime_frame.png"))
                                _sh.copyfile(str(right), str(dst/"accuracy_frame.png"))
                                did_ab = True
                        else:
                            try:
                                client.ab_compare(mp4)
                                did_ab = True
                            except Exception:
                                # Fallback: try data/offline assets
                                off = _P("data/offline")
                                dst = _P("runs/latest"); dst.mkdir(parents=True, exist_ok=True)
                                left = off/"realtime_frame.png"; right = off/"accuracy_frame.png"
                                if left.exists() and right.exists():
                                    _sh.copyfile(str(left), str(dst/"realtime_frame.png"))
                                    _sh.copyfile(str(right), str(dst/"accuracy_frame.png"))
                                    did_ab = True
                        if did_ab:
                            st.session_state["show_ab"] = True
                            st.session_state["has_run"] = True
                            st.success("Compare images ready. Use the slider below.")
                        else:
                            st.info("Compare prepared. Slider will appear when images are available.")
                with a3:
                    if running and st.button("Stop run", use_container_width=True, help="Cancel the active run"):
                        try:
                            client.run_control("stop")
                            st.toast("Stopped.", icon="⏹️")
                        except Exception as e:
                            st.warning(f"Stop failed: {e}")
                with a4:
                    if has_artifacts and st.button("Clear Results", use_container_width=True, help="Remove artifacts and telemetry for a fresh run"):
                        try:
                            client.clear()
                        except Exception:
                            pass
                        st.session_state["show_ab"] = False
                        st.session_state["has_run"] = False
                        st.session_state["has_artifacts"] = False
                        st.session_state["telemetry_rows"] = []
                        st.toast("Cleared.", icon="🧹")
                st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

                # P1: quick metrics & report
                b1, b2 = st.columns([1.2,1.6])
                with b1:
                    if st.button("Compute metrics", use_container_width=True, disabled=not st.session_state.get("has_run"), help="Compute simple metrics from events.jsonl"):
                        try:
                            import json as _json
                            from pathlib import Path as _P
                            evp = _P("runs/latest/events.jsonl")
                            frames = 0; fps_acc=0.0; pre=0.0; model=0.0; post=0.0
                            fps_list=[]; pre_list=[]; model_list=[]; post_list=[]
                            if evp.exists():
                                with evp.open("r", encoding="utf-8") as fh:
                                    for line in fh:
                                        try:
                                            ev = _json.loads(line)
                                            frames += 1
                                            fps_acc += float(ev.get("fps") or 0)
                                            pre += float(ev.get("pre_ms") or 0)
                                            model += float(ev.get("model_ms") or 0)
                                            post += float(ev.get("post_ms") or 0)
                                            fps_list.append(float(ev.get("fps") or 0))
                                            pre_list.append(float(ev.get("pre_ms") or 0))
                                            model_list.append(float(ev.get("model_ms") or 0))
                                            post_list.append(float(ev.get("post_ms") or 0))
                                        except Exception:
                                            continue
                            def p95(vals):
                                vals = sorted(vals)
                                if not vals: return 0.0
                                k = int(0.95*(len(vals)-1))
                                return round(vals[k],2)
                            metrics = {
                                "frames": frames,
                                "avg_fps": round((fps_acc/frames) if frames else 0, 2),
                                "avg_pre_ms": round((pre/frames) if frames else 0, 2),
                                "avg_model_ms": round((model/frames) if frames else 0, 2),
                                "avg_post_ms": round((post/frames) if frames else 0, 2),
                                "p95_fps": p95(fps_list),
                                "p95_pre_ms": p95(pre_list),
                                "p95_model_ms": p95(model_list),
                                "p95_post_ms": p95(post_list),
                            }
                            _P("runs/latest").mkdir(parents=True, exist_ok=True)
                            with _P("runs/latest/metrics.json").open("w", encoding="utf-8") as fh:
                                _json.dump(metrics, fh, indent=2)
                            st.toast("Metrics computed.", icon="📊")
                            # Inline metrics card
                            st.markdown("<div class='card'>", unsafe_allow_html=True)
                            st.markdown(f"**Frames**: {metrics['frames']}  ")
                            st.markdown(f"**FPS (avg/95p)**: {metrics['avg_fps']} / {metrics['p95_fps']}  ")
                            st.markdown(f"**Latency avg (ms)**: pre {metrics['avg_pre_ms']} | model {metrics['avg_model_ms']} | post {metrics['avg_post_ms']}")
                            st.markdown(f"**Latency 95p (ms)**: pre {metrics['p95_pre_ms']} | model {metrics['p95_model_ms']} | post {metrics['p95_post_ms']}")
                            st.markdown("</div>", unsafe_allow_html=True)
                            # Show profile badges summary next to link
                            _inp = st.session_state.get("last_profile_input", None) or (640 if st.session_state.get("profile_mode_focus","realtime")=="realtime" else 1024)
                            _conf = float(st.session_state.get("conf_thresh_focus", 0.35))
                            _nms = float(st.session_state.get("nms_iou_focus", 0.5))
                            st.caption(f"Input {_inp} · Conf ≥ {_conf:.2f} · NMS IoU {_nms:.2f}  |  View full metrics → Metrics tab  |  Export: runs/latest/metrics.json")
                        except Exception as e:
                            st.warning(f"Scoring failed: {e}")
                with b2:
                    if st.button("Generate report (PDF)", use_container_width=True, disabled=not st.session_state.get("has_run"), help="Save a brief PDF with summary and last frame"):
                        try:
                            from PIL import Image as PILImage, ImageDraw
                            out_pdf = Path("runs/latest/report.pdf")
                            lf = Path("runs/latest/last_frame.png")
                            if lf.exists():
                                im = PILImage.open(lf).convert("RGB").resize((1280,720))
                                page = PILImage.new("RGB", (1280, 900), (6,15,37))
                                d = ImageDraw.Draw(page)
                                d.text((40,30), "PerceptionLab — Run summary", fill=(200,245,255))
                                page.paste(im, (0,160))
                                out_pdf.parent.mkdir(parents=True, exist_ok=True)
                                page.save(out_pdf, "PDF", resolution=144)
                                st.toast("Report ready.", icon="📄")
                            else:
                                st.info("No last_frame.png to include in report.")
                        except Exception as e:
                            st.warning(f"Report generation failed: {e}")

                # Overlays & thresholds
                st.markdown("### Overlays & thresholds")
                ov1, ov2, ov3, ov4 = st.columns([1,1,1,1])
                with ov1:
                    show_boxes = st.checkbox("Boxes", value=True, key="ov_boxes_focus")
                with ov2:
                    show_tracks = st.checkbox("Tracks", value=True, key="ov_tracks_focus")
                with ov3:
                    show_ocr = st.checkbox("OCR", value=True, key="ov_ocr_focus")
                with ov4:
                    st.session_state["show_hud"] = st.checkbox("HUD", value=st.session_state.get("show_hud", False), key="ov_hud_focus")

                with st.expander("Advanced thresholds", expanded=False):
                    mask_opacity = st.slider("Mask opacity", 0.0, 1.0, st.session_state.get("mask_opacity_focus", 0.35), 0.05, help="Transparency of segmentation overlays", key="mask_opacity_focus")
                    c1, c2 = st.columns(2)
                    with c1:
                        conf_thresh = st.slider("Confidence", 0.05, 0.95, st.session_state.get("conf_thresh_focus", 0.35), 0.05, help="Filter low-score detections.", key="conf_thresh_focus")
                    with c2:
                        nms_iou = st.slider("NMS IoU", 0.05, 0.95, st.session_state.get("nms_iou_focus", 0.5), 0.05, help="Merge overlapping boxes.", key="nms_iou_focus")
                    class_filter = st.text_input("Class include (comma-separated)", value=st.session_state.get("class_filter_focus", ""), help="Limit overlays to these classes", key="class_filter_focus")
                    if st.button("Reset to defaults", use_container_width=False):
                        st.session_state.update(mask_opacity_focus=0.35, conf_thresh_focus=0.35, nms_iou_focus=0.5, class_filter_focus="", ov_boxes_focus=True, ov_tracks_focus=True, ov_ocr_focus=True)
                        st.toast("Thresholds reset.", icon="↩️")
                    if st.button("Apply & re‑run", use_container_width=False, disabled=disabled_common):
                        try:
                            overlays = {
                                "boxes": st.session_state.get("ov_boxes_focus", True),
                                "tracks": st.session_state.get("ov_tracks_focus", True),
                                "ocr": st.session_state.get("ov_ocr_focus", True),
                                "hud": st.session_state.get("ov_hud_focus", False),
                            }
                            thresholds = {
                                "confidence": st.session_state.get("conf_thresh_focus", 0.35),
                                "nms_iou": st.session_state.get("nms_iou_focus", 0.5),
                                "mask_opacity": st.session_state.get("mask_opacity_focus", 0.35),
                                "include": st.session_state.get("class_filter_focus", ""),
                            }
                            client.run_video(mp4, profile, duration_s=10, emit_video=False, overlays=overlays, thresholds=thresholds)
                            st.session_state["has_run"] = True
                            st.toast("Re‑run complete.", icon="🔁")
                        except Exception as e:
                            st.warning(f"Re‑run failed: {e}")
                st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

                # A/B slider section
                st.markdown("### Profile compare (single frame)")
                from pathlib import Path as _P
                rt_img = _P("runs/latest/realtime_frame.png")
                ac_img = _P("runs/latest/accuracy_frame.png")
                if st.session_state.get("show_ab") and rt_img.exists() and ac_img.exists():
                    try:
                        from streamlit_image_comparison import image_comparison
                        # Constrain slider width so it fits within the left column without overlapping
                        image_comparison(img1=str(rt_img), img2=str(ac_img), label1="Realtime", label2="Accuracy", width=520)
                        if st.button("Save composite"):
                            try:
                                from PIL import Image as PILImage
                                L = PILImage.open(rt_img)
                                R = PILImage.open(ac_img)
                                composite = PILImage.new("RGB", L.size)
                                composite.paste(L, (0,0))
                                composite.paste(R, (L.width//2,0))
                                out_path = _P("runs/latest/ab_composite.png")
                                composite.save(out_path)
                                st.success(f"Saved {out_path}")
                            except Exception as e:
                                st.warning(f"Save failed: {e}")
                        st.caption("Realtime (left) — Accuracy (right)")
                    except Exception:
                        st.info("A/B slider requires 'streamlit-image-comparison'. Install: pip install streamlit-image-comparison")
                else:
                    st.caption("Click 'Compare this frame' to populate.")

                # Telemetry compact table
                if st.session_state.get("has_run") and Path("runs/latest/events.jsonl").exists():
                    st.markdown("### Telemetry")
                    # Prefer reading events.jsonl if present
                    rows = []
                    try:
                        from pathlib import Path as _P
                        ev_path = _P("runs/latest/events.jsonl")
                        if ev_path.exists():
                            import json as _json
                            with ev_path.open("r", encoding="utf-8") as fh:
                                for line in fh.readlines()[-200:]:
                                    try:
                                        ev = _json.loads(line.strip())
                                        rows.append({
                                            "frame_id": ev.get("frame_id"),
                                            "fps": ev.get("fps"),
                                            "pre_ms": (ev.get("latency_ms") or {}).get("pre"),
                                            "model_ms": (ev.get("latency_ms") or {}).get("model"),
                                            "post_ms": (ev.get("latency_ms") or {}).get("post"),
                                            "provider": (ev.get("provider_provenance") or {}).get("detector"),
                                            "level": ev.get("level", "info"),
                                        })
                                    except Exception:
                                        continue
                            # update HUD snapshot from last row
                            if rows:
                                last = rows[-1]
                                st.session_state["hud_vals"] = {"fps": last.get("fps"), "pre": last.get("pre_ms"), "model": last.get("model_ms"), "post": last.get("post_ms")}
                    except Exception:
                        rows = st.session_state.get("telemetry_rows", [])
                    errors_only = st.checkbox("Errors only", key="telemetry_errors_only")
                    view_rows = rows
                    if errors_only:
                        view_rows = [r for r in rows if r.get("level") in ["warn","error","timeout"]]
                    if view_rows:
                        import pandas as pd
                        df = pd.DataFrame(view_rows)[["frame_id","fps","pre_ms","model_ms","post_ms","provider","level"]]
                        st.dataframe(df.tail(100), use_container_width=True, height=240)
                    else:
                        if st.session_state.get("is_running"):
                            st.markdown("<div class='skeleton'></div>", unsafe_allow_html=True)
                        else:
                            st.caption("No telemetry yet.")

                # Artifacts panel (moved to right column)
                if not rendered_side_panels:
                    st.markdown("### Artifacts")
                last_frame = _P("runs/latest/last_frame.png")
                ab_comp = _P("runs/latest/ab_composite.png")
                out_mp4 = _P("runs/latest/out.mp4")
                report_pdf = _P("runs/latest/report.pdf")
                ac1, ac2 = st.columns([1,1])
                if (has_artifacts) and (not rendered_side_panels):
                    with ac1:
                        if last_frame.exists():
                            st.image(str(last_frame), caption="last_frame.png", use_column_width=True)
                            cpl, cpr = st.columns([1,3])
                            with cpl:
                                if st.button("Copy path (image)"):
                                    st.info(str(last_frame))
                        if ab_comp.exists():
                            st.image(str(ab_comp), caption="ab_composite.png", use_column_width=True)
                            if st.button("Copy path (composite)"):
                                st.info(str(ab_comp))
                    with ac2:
                        if out_mp4.exists():
                            st.video(str(out_mp4))
                            if st.button("Copy path (video)"):
                                st.info(str(out_mp4))
                        if report_pdf.exists():
                            st.link_button("Open report (PDF)", report_pdf.as_posix(), use_container_width=True)
                            if st.button("Copy path (report)"):
                                st.info(str(report_pdf))
                    st.caption("Artifacts reflect the current mode and overlay settings at capture time.")
                else:
                    if st.session_state.get("is_running"):
                        st.markdown("<div class='skeleton'></div>", unsafe_allow_html=True)
                    else:
                        if not rendered_side_panels:
                            st.caption("Artifacts appear here after a run or compare.")

                # Inline missing asset warning
                if not mp4_ok:
                    st.warning(f"Source missing: {mp4}")

                # Keyboard shortcuts: space (Run 10s), b (Compare), esc (Back)
                st.markdown(
                    """
                    <script>
                    document.addEventListener('keydown', function(e){
                      const buttons = [...document.querySelectorAll('button')];
                      function clickByText(t){ const el = buttons.find(b => (b.innerText||'').trim()===t); if(el){ e.preventDefault(); el.click(); return true;} return false; }
                      if(e.code==='Space'){ clickByText('Run 10s'); }
                      if(e.key==='b' || e.key==='B'){ if(!clickByText('Save composite')){ clickByText('Compare this frame'); } }
                      if(e.key==='Escape'){ const el = buttons.find(b => (b.innerText||'').includes('Back to gallery')); if(el){ e.preventDefault(); el.click(); }}
                    });
                    </script>
                    """,
                    unsafe_allow_html=True,
                )
                # Hidden Bookmark button and list moved to right column

                # Note: Single-image tools have been removed from the focus view per requirements.

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
        # Reports (merged into Evaluate)
        st.markdown("---")
        st.subheader("Reports")
        run_id = st.text_input("Run ID", value="2025-09-02_12-00-00", key="eval_report_run_id")
        if st.button("Generate PDF", key="eval_report_generate"):
            try:
                resp = requests.post(f"{api_base}/report", json={"run_id": run_id}, timeout=10)
                st.success(resp.json())
            except Exception as e:
                st.warning(f"API not reachable yet: {e}")
        st.markdown("---")
        if st.button("Generate report for last run", key="eval_report_last"):
            try:
                last = requests.get(f"{api_base}/last_event", timeout=5).json()
                last_run = last.get("run_id")
                if not last_run:
                    st.info("No recent runs.")
                else:
                    resp = requests.post(f"{api_base}/report", json={"run_id": last_run}, timeout=20).json()
                    st.success(resp)
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

    with tab_monitor:
        st.subheader("Monitor")
        st.markdown("View Prometheus metrics at `/metrics`. Grafana default: http://localhost:3000")
        m1, m2 = st.columns([1,1])
        with m1:
            if st.button("Fetch /metrics"):
                try:
                    text = requests.get(f"{api_base}/metrics", timeout=5).text
                    st.code(text)
                except Exception as e:
                    st.warning(f"Metrics not available yet: {e}")
        with m2:
            st.link_button("Open /metrics", f"{api_base}/metrics", use_container_width=True)

        st.markdown("---")
        st.subheader("Providers readiness")
        if st.button("Refresh providers"):
            try:
                pr = requests.get(f"{api_base}/health/providers", timeout=3)
                if pr.ok:
                    data = pr.json()
                    # Render compact table if 'providers' mapping exists, else raw
                    prov = data.get("providers") if isinstance(data, dict) else None
                    if isinstance(prov, dict):
                        rows = []
                        for k, v in prov.items():
                            rows.append({"provider": k, "ready": bool(v)})
                        try:
                            import pandas as _pd
                            st.dataframe(_pd.DataFrame(rows), use_container_width=True, hide_index=True)
                        except Exception:
                            st.json(rows)
                    else:
                        st.json(data)
                else:
                    st.info("/health/providers not available.")
            except Exception as e:
                st.warning(f"Providers check failed: {e}")
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

    # Reports tab removed; its content was merged into Evaluate

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

    # Use Cases tab removed per request
        # Make the Use Cases tab labels smaller to avoid overlap (scoped via JS-assigned class)
        st.markdown(
            """
            <script>
            (function(){
              const titles = [
                'Roadway Traffic & Sign Intelligence',
                'Warehouse Safety & PPE',
                'Retail Shelf QA (OCR)',
                'Smart City Anomaly & Flow',
                'Agriculture Field Scan'
              ];
              const lists = Array.from(document.querySelectorAll('section.main div[role="tablist"]'));
              for (const tl of lists){
                const labels = Array.from(tl.querySelectorAll('button p')).map(p=> (p.innerText||'').trim());
                // Heuristic: if any expected title appears, tag this tablist
                if (labels.some(l=> titles.some(t=> l.startsWith(t.substring(0,6))))){
                  tl.classList.add('use-cases-tabs');
                }
              }
            })();
            </script>
            <style>
              .use-cases-tabs button p { font-size: 11px !important; line-height: 1.15; font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
              .use-cases-tabs button { padding-top: 2px !important; padding-bottom: 2px !important; max-width: 100%; }
              .use-cases-tabs { gap: 4px !important; }
            </style>
            """,
            unsafe_allow_html=True,
        )
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


