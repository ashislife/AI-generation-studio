
import os
from urllib.parse import urljoin

import requests
import streamlit as st

st.set_page_config(
    page_title="AI Generation Studio",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

API = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")

# Premium compact UI
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

:root {
    --bg: #090d18;
    --panel: #111827;
    --border: #293449;
    --muted: #94a3b8;
    --purple: #8b5cf6;
    --cyan: #22d3ee;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background:
        radial-gradient(ellipse at 12% 0%, #20183c 0%, transparent 32%),
        radial-gradient(ellipse at 90% 5%, #102a3a 0%, transparent 28%),
        var(--bg);
    color: #f1f5f9;
}

[data-testid="stHeader"] {
    background: transparent;
    height: 2rem;
}

.block-container {
    max-width: 1400px;
    padding-top: 0.5rem;
    padding-bottom: 1.5rem;
}

h1, h2, h3 {
    font-family: 'Space Grotesk', sans-serif !important;
    letter-spacing: -0.035em;
}

section[data-testid="stSidebar"] {
    background: #0c111e;
    border-right: 1px solid var(--border);
}

section[data-testid="stSidebar"] > div {
    padding-top: 1rem;
}

.brand {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 16px;
}

.brand-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 39px;
    height: 39px;
    border-radius: 12px;
    background: linear-gradient(135deg, #7c3aed, #0891b2);
    color: white;
    font-size: 22px;
}

.brand-name {
    color: white;
    font-size: 17px;
    font-weight: 700;
}

.brand-sub {
    color: var(--muted);
    font-size: 10px;
    letter-spacing: 1.4px;
    margin-top: 2px;
}

.hero {
    padding: 22px 28px;
    border-radius: 20px;
    border: 1px solid #343750;
    background: linear-gradient(115deg, #1b1c35, #14263b 75%, #14283b);
    margin-bottom: 16px;
}

.eyebrow {
    color: #c4b5fd;
    font-size: 10px;
    letter-spacing: 2px;
    font-weight: 700;
    text-transform: uppercase;
}

.hero h1 {
    font-size: clamp(27px, 3vw, 36px);
    line-height: 1.15;
    margin: 8px 0;
    color: white;
}

.hero p {
    color: #b7c2d5;
    font-size: 14px;
    line-height: 1.5;
    margin-bottom: 0;
    max-width: 720px;
}

.pills {
    display: flex;
    flex-wrap: wrap;
    gap: 7px;
    margin-top: 13px;
}

.pill {
    display: inline-block;
    border: 1px solid #3b4560;
    background: #111a2a;
    color: #dbe5f7;
    border-radius: 20px;
    padding: 5px 10px;
    font-size: 11px;
}

.metric {
    background: rgba(17, 24, 39, 0.9);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 13px 16px;
    min-height: 75px;
    margin-bottom: 15px;
}

.metric-label {
    color: var(--muted);
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 1.3px;
}

.metric-value {
    color: #f8fafc;
    font-size: 15px;
    font-weight: 700;
    margin-top: 7px;
}

.section-heading {
    font-family: 'Space Grotesk', sans-serif;
    color: #f8fafc;
    font-size: 19px;
    font-weight: 700;
    margin: 2px 0 12px;
}

.stTextArea textarea,
.stTextInput input {
    background: #0b1120 !important;
    color: #f8fafc !important;
    border: 1px solid #344054 !important;
    border-radius: 11px !important;
}

.stTextArea textarea:focus,
.stTextInput input:focus {
    border-color: var(--purple) !important;
    box-shadow: 0 0 0 1px var(--purple) !important;
}

div[data-baseweb="select"] > div {
    background: #0b1120;
    border-color: #344054;
    border-radius: 10px;
}

.stButton > button[kind="primary"] {
    min-height: 46px;
    border: 0;
    border-radius: 11px;
    color: white;
    font-weight: 700;
    background: linear-gradient(100deg, #7c3aed, #4f46e5, #0891b2);
    box-shadow: 0 5px 18px rgba(99, 102, 241, 0.16);
    transition: filter .15s ease;
}

.stButton > button[kind="primary"]:hover {
    filter: brightness(1.12);
}

.stDownloadButton > button {
    width: 100%;
    min-height: 42px;
    border-radius: 10px;
    border: 1px solid #6552a4;
    background: #201b38;
    color: white;
    font-weight: 600;
}

.preview {
    min-height: 280px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    border: 1px dashed #3a4560;
    border-radius: 16px;
    background: rgba(13, 20, 34, 0.85);
    padding: 24px;
}

.preview-icon {
    font-size: 38px;
    margin-bottom: 10px;
}

.preview-title {
    font-size: 17px;
    font-weight: 700;
    color: #e5e7eb;
}

.preview-text {
    color: var(--muted);
    font-size: 12px;
    line-height: 1.6;
    max-width: 320px;
    margin-top: 7px;
}

.status {
    color: #a5b4fc;
    font-size: 11px;
    overflow-wrap: anywhere;
}

div[data-testid="stAlert"] {
    border-radius: 11px;
}

footer {
    visibility: hidden;
}

@media (max-width: 800px) {
    .block-container {
        padding: 0.5rem 1rem 1.5rem;
    }
    .hero {
        padding: 20px;
    }
}
</style>
""", unsafe_allow_html=True)


# Sidebar settings
with st.sidebar:
    st.markdown("""
    <div class="brand">
        <div class="brand-icon">✦</div>
        <div>
            <div class="brand-name">Generation Studio</div>
            <div class="brand-sub">CREATIVE AI WORKSPACE</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("### Generation settings")

    mode = st.radio("Create", ["Image", "Video"])
    is_video = mode == "Video"

    if is_video:
        steps = st.slider("Inference steps", 1, 12, 4)
        guidance = st.slider("Guidance scale", 0.5, 5.0, 1.5, 0.5)
        frames = st.slider("Frames", 4, 16, 8, 4)
        size = st.selectbox("Resolution", [192, 256, 384, 512], index=1)
        st.caption("Short clips · AnimateLCM")
    else:
        steps = st.slider("Inference steps", 10, 30, 20, 5)
        guidance = st.slider("Guidance scale", 5.0, 10.0, 7.5, 0.5)
        size = st.selectbox("Resolution", [256, 384, 512, 640, 768], index=2)
        st.caption("Text-to-image · Stable Diffusion")

    seed = st.number_input(
        "Seed", min_value=0, max_value=4294967295, value=42, step=1
    )

    with st.expander("Advanced settings"):
        negative = st.text_area(
            "Negative prompt",
            "blurry, low quality, distorted, deformed, watermark, text",
            height=90,
        )

    st.divider()

    try:
        health_response = requests.get(f"{API}/health", timeout=4)
        health_response.raise_for_status()
        health = health_response.json()

        if health.get("cuda_available"):
            st.success(f"GPU connected · {health.get('gpu_name', 'CUDA ready')}")
        else:
            st.warning("Backend online · CPU only")
    except requests.RequestException:
        st.error("Backend offline")

    st.markdown(
        f'<div class="status">Backend API<br>{API}</div>',
        unsafe_allow_html=True,
    )


# Compact hero
st.markdown("""
<div class="hero">
    <div class="eyebrow">AI-powered creative workspace</div>
    <h1>Turn ideas into visual experiences.</h1>
    <p>
        Generate beautiful images and cinematic short videos from text.
        Customize your settings, preview your creation, and download your result.
    </p>
    <div class="pills">
        <span class="pill">✦ Text to image</span>
        <span class="pill">◉ Text to video</span>
        <span class="pill">⚡ GPU-powered inference</span>
    </div>
</div>
""", unsafe_allow_html=True)


# Summary cards
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="metric">
        <div class="metric-label">Workspace</div>
        <div class="metric-value">AI Generation Studio</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    output_type = "Video · MP4" if is_video else "Image · PNG"
    st.markdown(f"""
    <div class="metric">
        <div class="metric-label">Output format</div>
        <div class="metric-value">{output_type}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric">
        <div class="metric-label">Resolution</div>
        <div class="metric-value">{size} × {size}</div>
    </div>
    """, unsafe_allow_html=True)


# Prompt and preview
left, right = st.columns([1, 1], gap="large")

with left:
    st.markdown(
        '<div class="section-heading">01 · Describe your creation</div>',
        unsafe_allow_html=True,
    )

    prompt = st.text_area(
        "Prompt",
        placeholder=(
            "A cinematic waterfall flowing through a lush green forest "
            "at golden hour, realistic lighting, fine details..."
        ),
        height=150,
    )

    st.caption("Tip: Describe the subject, environment, lighting, and style.")

    generate_clicked = st.button(
        "✦  Generate video" if is_video else "✦  Generate image",
        type="primary",
        use_container_width=True,
    )

with right:
    st.markdown(
        '<div class="section-heading">02 · Preview and export</div>',
        unsafe_allow_html=True,
    )

    if "last_result" not in st.session_state:
        st.session_state.last_result = None

    result = st.session_state.last_result

    if result and result["mode"] == mode:
        if is_video:
            st.video(result["content"])
            st.download_button(
                "Download MP4",
                result["content"],
                file_name=result["filename"],
                mime="video/mp4",
                use_container_width=True,
            )
        else:
            st.image(
                result["content"],
                caption="Generated image",
                use_container_width=True,
            )
            st.download_button(
                "Download PNG",
                result["content"],
                file_name=result["filename"],
                mime="image/png",
                use_container_width=True,
            )
    else:
        icon = "🎬" if is_video else "✧"
        output = "video clip" if is_video else "image"

        st.markdown(f"""
        <div class="preview">
            <div class="preview-icon">{icon}</div>
            <div class="preview-title">Your {output} will appear here</div>
            <div class="preview-text">
                Enter a prompt, adjust the settings, and generate.
                Your result will appear here for preview and download.
            </div>
        </div>
        """, unsafe_allow_html=True)


# Generation
if generate_clicked:
    if not prompt.strip():
        st.warning("Please enter a prompt first.")
    else:
        payload = {
            "prompt": prompt.strip(),
            "negative_prompt": negative,
            "steps": int(steps),
            "guidance": float(guidance),
            "seed": int(seed),
            "width": int(size),
            "height": int(size),
        }

        if is_video:
            payload["frames"] = int(frames)
            payload["duration_seconds"] = 10

        endpoint = (
            f"{API}/api/generate/video"
            if is_video
            else f"{API}/api/generate/image"
        )

        try:
            with st.spinner(
                "Generating on the GPU server. The first run may take longer..."
            ):
                response = requests.post(
                    endpoint, json=payload, timeout=1800
                )

                if not response.ok:
                    try:
                        detail = response.json().get("detail", response.text)
                    except Exception:
                        detail = response.text

                    st.error(
                        f"Generation failed ({response.status_code}): {detail}"
                    )
                    st.stop()

                data = response.json()
                result_url = urljoin(
                    API + "/", data["url"].lstrip("/")
                )

                file_response = requests.get(result_url, timeout=180)
                file_response.raise_for_status()

            st.session_state.last_result = {
                "mode": mode,
                "filename": data.get("filename", "generated"),
                "content": file_response.content,
            }
            st.rerun()

        except requests.RequestException as exc:
            st.error(
                f"Cannot reach backend at {API}. "
                f"Check FastAPI and API_URL. Details: {exc}"
            )

st.divider()
st.caption(
    "AI Generation Studio · Set API_URL to your GPU backend URL for deployment."
)