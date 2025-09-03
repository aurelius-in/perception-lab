from __future__ import annotations

import time
from pathlib import Path

import streamlit as st


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
    st.write(
        "This is a branded shell UI. The full perception demo will be wired next."
    )


if __name__ == "__main__":
    main()


