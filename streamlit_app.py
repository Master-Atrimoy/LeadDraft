from __future__ import annotations

import html
import sys
from pathlib import Path
from typing import List

import requests
import streamlit as st

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from briefshift.core.config import load_settings
from briefshift.services.ollama_client import OllamaClient
from briefshift.services.rewriter import RewriteService
from briefshift.ui.theme import inject_theme


st.set_page_config(
    page_title="LeadDraft",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_theme()
settings = load_settings()
client = OllamaClient(
    base_url=settings.ollama_base_url,
    timeout_seconds=settings.request_timeout_seconds,
)
service = RewriteService(
    ollama_client=client,
    temperature=settings.temperature,
    top_p=settings.top_p,
    top_k=settings.top_k,
    keep_alive=settings.keep_alive,
)


STATE_DEFAULTS = {
    "active_view": "Draft",
    "workspace_choice": "Draft",
    "selected_model": settings.default_model,
    "model_select": settings.default_model,
    "latest_result": None,
    "pull_model_name": "",
}
for _k, _v in STATE_DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


@st.cache_data(ttl=10)
def fetch_models() -> List[str]:
    return client.list_models()


def set_view(view: str) -> None:
    st.session_state.active_view = view
    st.session_state.workspace_choice = view


def sync_workspace_choice() -> None:
    choice = st.session_state.get("workspace_choice", "Draft")
    set_view(choice)


def sync_model_select() -> None:
    st.session_state.selected_model = st.session_state.model_select


def render_text_block(title: str, body: str) -> None:
    safe_title = html.escape(title)
    safe_body = html.escape(body).replace("\n", "<br>")
    st.markdown(
        f"""
        <div class="output-block">
            <div class="output-block-title">{safe_title}</div>
            <div class="output-block-body">{safe_body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def resolve_runtime() -> tuple[bool, List[str]]:
    try:
        models = fetch_models()
        return True, models
    except requests.RequestException:
        return False, []


def render_header(online: bool, models: List[str]) -> None:
    left, right = st.columns([0.82, 0.18], gap="large")

    with left:
        st.markdown(
            f"""
            <section class="hero-shell">
                <h1>{html.escape(settings.name)}</h1>
                <p class="hero-subtitle">{html.escape(settings.tagline)}</p>
                <div class="hero-purpose">{html.escape(settings.purpose)}</div>
            </section>
            """,
            unsafe_allow_html=True,
        )

    with right:
        with st.popover("Model setup", icon=":material/tune:", use_container_width=True):
            st.caption("Local Ollama runtime")
            st.caption(settings.ollama_base_url)

            if st.button("Refresh models", use_container_width=True):
                fetch_models.clear()
                st.rerun()

            model_options = models[:] if models else [st.session_state.selected_model]
            if st.session_state.selected_model not in model_options:
                st.session_state.selected_model = model_options[0]
            if st.session_state.model_select not in model_options:
                st.session_state.model_select = st.session_state.selected_model

            st.selectbox(
                "Loaded model",
                options=model_options,
                key="model_select",
                on_change=sync_model_select,
                help="Choose a locally available Ollama model.",
            )

            model_to_pull = st.text_input(
                "Pull another model",
                key="pull_model_name",
                placeholder="qwen2.5:3b",
            )

            if st.button("Pull model", type="secondary", use_container_width=True):
                name = model_to_pull.strip()
                if not name:
                    st.warning("Enter a model name first.")
                else:
                    with st.spinner(f"Pulling {name}..."):
                        try:
                            client.pull_model(name)
                            fetch_models.clear()
                            st.session_state.selected_model = name
                            st.session_state.model_select = name
                            st.session_state.pull_model_name = ""
                            st.success(f"Added {name}")
                            st.rerun()
                        except requests.RequestException as exc:
                            st.error(f"Pull failed: {exc}")

        status_text = "Connected" if online else "Offline"
        model_text = st.session_state.selected_model if online else "Ollama unavailable"
        st.markdown(
            f"""
            <div class="runtime-card {'online' if online else 'offline'}">
                <div class="runtime-label">Runtime</div>
                <div class="runtime-status">{html.escape(status_text)}</div>
                <div class="runtime-model">{html.escape(model_text)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_workspace_switcher() -> None:
    st.radio(
        "Workspace",
        options=["Draft", "Rewrite"],
        horizontal=True,
        label_visibility="collapsed",
        key="workspace_choice",
        on_change=sync_workspace_choice,
    )


def render_draft_view() -> None:
    st.markdown("<div class='section-title'>Draft</div>", unsafe_allow_html=True)
    st.markdown("<div class='surface'>", unsafe_allow_html=True)

    raw_message = st.text_area(
        "Write your note",
        height=320,
        max_chars=settings.max_input_chars,
        placeholder="Example: We may miss the milestone because QA is blocked by unstable vendor credentials. Need to update my manager without sounding dramatic.",
        key="raw_message",
        label_visibility="collapsed",
    )

    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        audience = st.selectbox(
            "Audience",
            options=settings.audiences,
            index=settings.audiences.index(settings.default_audience),
            key="audience_select",
        )
    with c2:
        tone = st.selectbox(
            "Tone",
            options=settings.tones,
            index=settings.tones.index(settings.default_tone),
            key="tone_select",
        )
    with c3:
        length = st.selectbox(
            "Length",
            options=settings.lengths,
            index=settings.lengths.index(settings.default_length),
            key="length_select",
        )

    footer_left, footer_mid, footer_right = st.columns([0.22, 0.48, 0.30], gap="medium")
    with footer_left:
        include_subject = st.toggle("Include subject", value=True, key="include_subject")
    with footer_mid:
        st.markdown(
            "<div class='footer-note'>Refines tone, structure, and audience fit without changing the core message.</div>",
            unsafe_allow_html=True,
        )
    with footer_right:
        generate = st.button("Generate rewrite", type="primary", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    if generate:
        if not raw_message.strip():
            st.warning("Add a rough note first.")
            return

        with st.spinner("Generating rewrite..."):
            try:
                result = service.rewrite(
                    model=st.session_state.selected_model,
                    raw_message=raw_message,
                    audience=audience,
                    tone=tone,
                    length=length,
                    include_subject=include_subject,
                )
                st.session_state.latest_result = result.model_dump()
                set_view("Rewrite")
                st.rerun()
            except requests.RequestException as exc:
                st.error(f"Ollama request failed: {exc}")
            except Exception as exc:
                st.error(f"Rewrite failed: {exc}")


def render_rewrite_view() -> None:
    st.markdown("<div class='section-title'>Rewrite</div>", unsafe_allow_html=True)
    latest = st.session_state.latest_result

    if not latest:
        st.markdown(
            """
            <div class="empty-panel">
                <div class="empty-title">Nothing generated yet</div>
                <div class="empty-copy">Start in Draft, write a rough workplace note, and generate a cleaner rewrite.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    st.markdown("<div class='surface'>", unsafe_allow_html=True)

    meta_left, meta_right = st.columns([0.44, 0.56], gap="medium")
    with meta_left:
        if latest.get("subject_line"):
            st.markdown(
                f"<div class='meta-chip'><span>Subject</span>{html.escape(latest['subject_line'])}</div>",
                unsafe_allow_html=True,
            )
    with meta_right:
        st.markdown(
            f"<div class='meta-chip quiet'><span>Intent</span>{html.escape(latest['communication_goal'])}</div>",
            unsafe_allow_html=True,
        )

    recommended_tab, alternatives_tab, notes_tab = st.tabs(["Recommended", "Alternatives", "Notes"])

    with recommended_tab:
        render_text_block("Recommended rewrite", latest["primary_message"])

    with alternatives_tab:
        variants = latest.get("variants", [])
        if not variants:
            st.caption("No alternative rewrites returned.")
        else:
            for variant in variants:
                render_text_block(variant["label"], variant["message"])

    with notes_tab:
        notes = latest.get("editing_notes", [])
        if notes:
            note_markup = "".join(f"<li>{html.escape(note)}</li>" for note in notes)
            st.markdown(f"<ul class='notes-list'>{note_markup}</ul>", unsafe_allow_html=True)
        else:
            st.caption("No editing notes returned.")

    back_left, back_right = st.columns([0.74, 0.26], gap="medium")
    with back_left:
        st.markdown(
            "<div class='footer-note'>Adjust audience, tone, or length in Draft if you want another version.</div>",
            unsafe_allow_html=True,
        )
    with back_right:
        st.button("Back to draft", use_container_width=True, key="back_to_draft", on_click=lambda: set_view("Draft"))

    st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    online, models = resolve_runtime()

    if online and models:
        if st.session_state.selected_model not in models:
            st.session_state.selected_model = models[0]
        if st.session_state.model_select not in models:
            st.session_state.model_select = st.session_state.selected_model

    render_header(online=online, models=models)
    render_workspace_switcher()

    if st.session_state.active_view == "Draft":
        render_draft_view()
    else:
        render_rewrite_view()


if __name__ == "__main__":
    main()
