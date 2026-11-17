import os

import streamlit as st
from dotenv import load_dotenv

from translator import DEFAULT_MODEL, LANGUAGES, MAX_CHARS, TranslationError, translate

load_dotenv()

# Button caption per language (no flag emoji: Windows does not render them).
BUTTON_LABELS = {
    "영어": "영어 · English",
    "일본어": "일본어 · 日本語",
    "베트남어": "베트남어 · Tiếng Việt",
}

CSS = """
<style>
  .block-container { padding-top: 2.5rem; max-width: 760px; }
  h1 { font-size: 2rem !important; padding-bottom: 0 !important; }
  .app-sub { opacity: .65; margin: .25rem 0 1.25rem; }
  .counter { text-align: right; font-size: .85rem; opacity: .6; margin-top: -.25rem; }
  .counter.over { color: #d93025; opacity: 1; font-weight: 600; }
  .result-label { font-size: .85rem; font-weight: 600; opacity: .7; margin-bottom: .5rem; }
  .empty-state { opacity: .55; text-align: center; padding: 1.5rem 0; }
  div.stButton > button { min-height: 2.75rem; font-weight: 600; }
</style>
"""


def get_setting(name: str, default: str | None = None) -> str | None:
    """Read from .env/environment first, then st.secrets (deployment)."""
    value = os.getenv(name)
    if value:
        return value
    try:
        return st.secrets.get(name, default)
    except Exception:  # no secrets.toml present
        return default


st.set_page_config(page_title="AI 번역기", page_icon="🌐", layout="centered")
st.markdown(CSS, unsafe_allow_html=True)

st.title("🌐 AI 번역기")
st.markdown(
    '<p class="app-sub">글을 입력하고 번역할 언어를 선택하세요.</p>', unsafe_allow_html=True
)

with st.container(border=True):
    text = st.text_area(
        "번역할 글",
        height=180,
        placeholder="번역할 내용을 입력하세요. (한국어를 포함한 모든 언어 가능)",
    )
    over = len(text) > MAX_CHARS
    st.markdown(
        f'<div class="counter{" over" if over else ""}">{len(text):,} / {MAX_CHARS:,}자</div>',
        unsafe_allow_html=True,
    )

st.caption("번역할 언어 선택")
cols = st.columns(len(LANGUAGES))
clicked = None
for col, label in zip(cols, LANGUAGES):
    if col.button(BUTTON_LABELS[label], key=f"btn_{label}", use_container_width=True):
        clicked = label

if clicked:
    st.session_state.pop("result", None)
    st.session_state.pop("error", None)
    try:
        with st.spinner("번역 중..."):
            result = translate(
                text,
                LANGUAGES[clicked],
                get_setting("OPENAI_API_KEY"),
                get_setting("OPENAI_MODEL", DEFAULT_MODEL),
            )
        st.session_state["result"] = (clicked, result)
    except TranslationError as e:
        st.session_state["error"] = str(e)

st.markdown("##### 번역 결과")
with st.container(border=True):
    if "error" in st.session_state:
        st.warning(st.session_state["error"])
    elif "result" in st.session_state:
        label, result = st.session_state["result"]
        st.markdown(
            f'<div class="result-label">{BUTTON_LABELS[label]}</div>', unsafe_allow_html=True
        )
        st.code(result, language=None, wrap_lines=True)
    else:
        st.markdown(
            '<div class="empty-state">언어 버튼을 누르면 번역 결과가 여기에 표시됩니다.</div>',
            unsafe_allow_html=True,
        )
