import streamlit as st
import os, requests, time, random
from pathlib import Path
from moviepy.editor import ImageClip, VideoFileClip, AudioFileClip, concatenate_videoclips, vfx
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from streamlit_sortables import sort_items

# --- 1. SETTINGS & THEME ---
st.set_page_config(page_title="TITAN AI STUDIO", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #e6edf3; }
    .stButton>button { border-radius: 8px; background-color: #2e2e2e; color: white; border: 1px solid #444; font-weight: bold; }
    .stButton>button:hover { background-color: #ff4b4b; border: 1px solid #ff4b4b; }
    .stSlider { padding: 10px; }
    .timeline-clip { border: 1px solid #444; border-radius: 10px; padding: 12px; margin-bottom: 12px; background: #1f2937; }
    .timeline-clip:hover { border-color: #ff4b4b; background: #2d3748; }
    [data-testid="stHeader"] { background: rgba(0,0,0,0); }
    .block-container { padding-top: 1.5rem; }
    h1, h2, h3, h4 { color: #58a6ff; }
    </style>
    """, unsafe_allow_html=True)

for d in ["assets", "exports", "user_uploads"]:
    if not os.path.exists(d): os.makedirs(d)

if 'timeline' not in st.session_state:
    st.session_state.timeline = []
if 'audio_path' not in st.session_state:
    st.session_state.audio_path = None
if 'clip_counter' not in st.session_state:
    st.session_state.clip_counter = 0
if 'category_results' not in st.session_state:
    st.session_state.category_results = []
if 'ai_results' not in st.session_state:
    st.session_state.ai_results = []

CONTENT_CATEGORIES = {
    "Luxury Real Estate": [
        "luxury home exterior",
        "modern high-end kitchen",
        "luxury living room interior",
        "professional real estate agent handshake",
        "sunset city skyline branding"
    ],
    "Tech & Innovation": [
        "tech startup office",
        "AI technology visualization",
        "modern digital workspace",
        "software team collaboration",
        "futuristic innovation lab"
    ],
    "Corporate Business": [
        "corporate office meeting",
        "business executive presentation",
        "professional teamwork",
        "company growth concept",
        "office branding lifestyle"
    ],
    "Lifestyle & Travel": [
        "luxury travel destination",
        "premium lifestyle photoshoot",
        "vacation resort interior",
        "high-end fashion lifestyle",
        "travel adventure film"
    ]
}

AUDIO_LIBRARY = {
    "SoundHelix - Uplifting Corporate": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
    "SoundHelix - Ambient Corporate": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
    "SoundHelix - Energetic Groove": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
    "SoundHelix - Motivational Pop": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3"
}


def generate_placeholder_results(query, count=4):
    safe_query = query.replace(' ', '_').replace('/', '_')
    return [
        {
            "url": f"https://picsum.photos/seed/{safe_query}_{i}/1024/576",
            "prompt": f"Placeholder for {query}",
            "type": "placeholder"
        }
        for i in range(count)
    ]


def scrape_web_data(query):
    return generate_placeholder_results(query, count=4)


def render_waveform_preview(seed, length=24):
    bars = "▁▂▃▄▅▆▇█"
    rnd = random.Random(seed)
    return "".join(rnd.choice(bars) for _ in range(length))


def create_retry_session(total=5, backoff_factor=1):
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9"
    })
    retries = Retry(
        total=total,
        backoff_factor=backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"]
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


session = create_retry_session()


def download_remote_file(url, dest_path, timeout=30, allow_content_type=None):
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    response = session.get(url, timeout=timeout)
    response.raise_for_status()
    if allow_content_type:
        content_type = response.headers.get("Content-Type", "")
        if allow_content_type not in content_type:
            raise ValueError(f"Unexpected content type: {content_type}")
    with open(dest_path, "wb") as f:
        f.write(response.content)
    return dest_path


with st.container():
    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
    col1.title("🚀 TITAN STUDIO CapCut PRO")
    if 'mode' not in st.session_state:
        st.session_state.mode = "Assets"
    if col2.button("📥 ASSETS", use_container_width=True):
        st.session_state.mode = "Assets"
    if col3.button("✂️ EDITOR", use_container_width=True):
        st.session_state.mode = "Editor"
    if col4.button("🎵 AUDIO", use_container_width=True):
        st.session_state.mode = "Audio"
    if col5.button("📤 EXPORT", use_container_width=True):
        st.session_state.mode = "Export"

st.divider()

if st.session_state.mode == "Assets":
    st.subheader("📊 Asset Library - Scrape & Choose Content")
    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown("**Category Scraper**")
        category = st.selectbox("Select Category", list(CONTENT_CATEGORIES.keys()))
        if st.button("Load Category Assets", use_container_width=True):
            st.session_state.category_results = []
            for query in CONTENT_CATEGORIES[category]:
                scraped = scrape_web_data(query)
                st.session_state.category_results.extend(scraped)
            st.success(f"Loaded {len(st.session_state.category_results)} assets for {category}")

    with col_right:
        st.markdown("**AI Creative Prompt Generator**")
        topic = st.text_input("Enter Brand / Topic:", value="Luxury Real Estate")
        if st.button("Generate AI Scene Prompts", use_container_width=True):
            st.session_state.ai_results = []
            prompts = [
                f"Cinematic {topic} exterior scene",
                f"Luxury {topic} interior showcase",
                f"Professional {topic} lifestyle moment",
                f"Modern {topic} brand identity shot"
            ]
            for prompt in prompts:
                safe_prompt = prompt.replace(' ', '_').replace('/', '_')
                st.session_state.ai_results.append({
                    "url": f"https://picsum.photos/seed/ai_{safe_prompt}/1024/576",
                    "prompt": prompt,
                    "type": "ai"
                })
            st.success("Generated AI scene options.")

    if st.session_state.category_results:
        st.subheader("📸 Scraped Results")
        cols = st.columns(4)
        for idx, asset in enumerate(st.session_state.category_results):
            with cols[idx % 4]:
                st.image(asset['url'], width=180)
                if st.button("Add to Timeline", key=f"add_scraped_{idx}", use_container_width=True):
                    st.session_state.clip_counter += 1
                    st.session_state.timeline.append({
                        "id": st.session_state.clip_counter,
                        "url": asset['url'],
                        "duration": 4,
                        "speed": 1.0,
                        "type": "image"
                    })
                    st.success("Added to timeline")

    if st.session_state.ai_results:
        st.subheader("🤖 AI Generated Scenes")
        cols = st.columns(4)
        for idx, asset in enumerate(st.session_state.ai_results):
            with cols[idx % 4]:
                st.image(asset['url'], width=180)
                st.caption(asset['prompt'])
                if st.button("Add to Timeline", key=f"add_ai_{idx}", use_container_width=True):
                    st.session_state.clip_counter += 1
                    st.session_state.timeline.append({
                        "id": st.session_state.clip_counter,
                        "url": asset['url'],
                        "duration": 5,
                        "speed": 1.0,
                        "type": "image"
                    })
                    st.success("Added AI scene to timeline")

elif st.session_state.mode == "Editor":
    st.subheader("✂️ CapCut-Style Editor")
    upload_col, info_col = st.columns([1, 1])
    with upload_col:
        st.markdown("**Import / Upload Clips**")
        uploaded_files = st.file_uploader(
            "Upload images or video clips:",
            type=["jpg", "jpeg", "png", "mp4", "mov"],
            accept_multiple_files=True
        )
        if uploaded_files:
            for uploaded in uploaded_files:
                local_path = Path("user_uploads") / uploaded.name
                with open(local_path, "wb") as f:
                    f.write(uploaded.getbuffer())
                extension = local_path.suffix.lower()
                clip_type = "video" if extension in [".mp4", ".mov"] else "image"
                st.session_state.clip_counter += 1
                st.session_state.timeline.append({
                    "id": st.session_state.clip_counter,
                    "url": str(local_path),
                    "duration": 5,
                    "speed": 1.0,
                    "type": clip_type
                })
            st.success("Uploaded clips added to the editor.")

    with info_col:
        total_duration = sum(clip['duration'] / clip['speed'] for clip in st.session_state.timeline) if st.session_state.timeline else 0
        st.metric("Clips in Timeline", len(st.session_state.timeline))
        st.metric("Total Duration", f"{total_duration:.1f}s")
        st.metric("Audio Loaded", "Yes" if st.session_state.audio_path else "No")

    if st.session_state.timeline:
        st.subheader("🧩 Timeline Reorder")
        reorder_items = [
            f"{clip['id']}|{clip['type']}|{Path(clip['url']).name}"
            for clip in st.session_state.timeline
        ]
        sorted_items = sort_items(
            reorder_items,
            header="Drag clips to reorder the timeline",
            direction="vertical",
            custom_style=".sortable-item { padding: 12px; border-radius: 8px; background-color: #171f2f; color: #e6edf3; margin-bottom: 8px; border: 1px solid #444; } .sortable-item:hover { background-color: #2e3a56; } .sortable-component { background: transparent; }",
            key="timeline_sorter"
        )
        if sorted_items != reorder_items:
            clip_by_id = {str(clip['id']): clip for clip in st.session_state.timeline}
            st.session_state.timeline = [
                clip_by_id[item.split('|', 1)[0]]
                for item in sorted_items
                if item.split('|', 1)[0] in clip_by_id
            ]

        st.subheader("🧩 Dedicated Timeline Board")
        rows = (len(st.session_state.timeline) + 3) // 4
        board = [st.columns(4) for _ in range(rows)]
        for idx, clip in enumerate(st.session_state.timeline):
            col = board[idx // 4][idx % 4]
            with col:
                st.markdown(f"**☰ Clip {idx + 1}**")
                if clip['type'] == 'image':
                    try:
                        st.image(clip['url'], use_column_width=True)
                    except:
                        st.write("Preview unavailable")
                else:
                    st.write(f"🎬 {Path(clip['url']).name}")
                st.markdown(f"**Duration:** {clip['duration']}s  |  **Speed:** {clip['speed']}x")
                waveform = render_waveform_preview(clip['id'] * int(clip['duration'] * 10 + 1))
                st.markdown(f"`{waveform}`")
                if st.button("⬆️", key=f"up_card_{clip['id']}", use_container_width=True) and idx > 0:
                    st.session_state.timeline[idx - 1], st.session_state.timeline[idx] = st.session_state.timeline[idx], st.session_state.timeline[idx - 1]
                    st.experimental_rerun()
                if st.button("⬇️", key=f"down_card_{clip['id']}", use_container_width=True) and idx < len(st.session_state.timeline) - 1:
                    st.session_state.timeline[idx + 1], st.session_state.timeline[idx] = st.session_state.timeline[idx], st.session_state.timeline[idx + 1]
                    st.experimental_rerun()

        st.divider()
        st.subheader("🎞️ Clip Controls")
        for i, clip in enumerate(st.session_state.timeline):
            with st.container():
                st.markdown(f"<div class='timeline-clip'>", unsafe_allow_html=True)
                cols = st.columns([1, 2, 1])
                with cols[0]:
                    if clip['type'] == 'image':
                        try:
                            st.image(clip['url'], width=200)
                        except:
                            st.write("Preview unavailable")
                    else:
                        st.write(f"🎬 Video clip: {Path(clip['url']).name}")
                with cols[1]:
                    st.write(f"**Clip #{clip['id']}** — {clip['type'].upper()}")
                    clip['duration'] = st.slider(
                        f"Duration (s)", 1, 15, int(clip['duration']), key=f"duration_{clip['id']}"
                    )
                    clip['speed'] = st.slider(
                        f"Speed", 0.25, 2.0, float(clip['speed']), step=0.25, key=f"speed_{clip['id']}"
                    )
                    st.write(f"Duration after speed: {clip['duration'] / clip['speed']:.1f}s")
                    waveform = render_waveform_preview(clip['id'] * int(clip['duration'] * 10 + 1), length=32)
                    st.markdown(f"`{waveform}`")
                with cols[2]:
                    if st.button("⬆️ Move Up", key=f"move_up_{clip['id']}", use_container_width=True) and i > 0:
                        st.session_state.timeline[i-1], st.session_state.timeline[i] = st.session_state.timeline[i], st.session_state.timeline[i-1]
                        st.experimental_rerun()
                    if st.button("⬇️ Move Down", key=f"move_down_{clip['id']}", use_container_width=True) and i < len(st.session_state.timeline) - 1:
                        st.session_state.timeline[i+1], st.session_state.timeline[i] = st.session_state.timeline[i], st.session_state.timeline[i+1]
                        st.experimental_rerun()
                    if st.button("🗑️ Delete", key=f"delete_{clip['id']}", use_container_width=True):
                        st.session_state.timeline.pop(i)
                        st.experimental_rerun()
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("Your timeline is empty. Add scenes from ASSETS or upload clips.")

elif st.session_state.mode == "Audio":
    st.subheader("🎵 Audio Sync & Library")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Free Audio Library**")
        choice = st.selectbox("Choose a free track:", list(AUDIO_LIBRARY.keys()))
        if st.button("Load Selected Audio", use_container_width=True):
            audio_url = AUDIO_LIBRARY[choice]
            try:
                audio_path = download_remote_file(audio_url, Path("assets") / "bg.mp3", allow_content_type="audio")
                st.session_state.audio_path = str(audio_path)
                st.success("Audio loaded successfully")
            except Exception as e:
                st.session_state.audio_path = None
                st.error(f"Failed to load audio: {type(e).__name__}: {e}")
    with col2:
        st.markdown("**Upload Your Own Audio**")
        uploaded_audio = st.file_uploader("Upload MP3/WAV audio", type=["mp3", "wav", "m4a"])
        if uploaded_audio:
            audio_path = Path("user_uploads") / uploaded_audio.name
            with open(audio_path, "wb") as f:
                f.write(uploaded_audio.getbuffer())
            st.session_state.audio_path = str(audio_path)
            st.success(f"Loaded {uploaded_audio.name}")
    if st.session_state.audio_path:
        st.audio(st.session_state.audio_path)
        st.write(f"Current audio: {st.session_state.audio_path}")
        st.write("**Audio Waveform Preview**")
        waveform = render_waveform_preview(sum(ord(c) for c in st.session_state.audio_path), length=64)
        st.markdown(f"`{waveform}`")

elif st.session_state.mode == "Export":
    st.subheader("🚀 Export Production")
    if not st.session_state.timeline:
        st.error("No clips in timeline. Add assets or uploaded clips first.")
    else:
        total_clips = len(st.session_state.timeline)
        total_duration = sum(clip['duration'] / clip['speed'] for clip in st.session_state.timeline)
        st.metric("Clip count", total_clips)
        st.metric("Final duration", f"{total_duration:.1f}s")
        st.metric("Audio", "Loaded" if st.session_state.audio_path else "None")

        if st.button("Render Final Video", use_container_width=True):
            with st.spinner("Rendering video, please wait..."):
                output_path = Path("exports") / f"TITAN_Ad_{int(time.time())}.mp4"
                final_clips = []
                for idx, clip in enumerate(st.session_state.timeline):
                    if clip['type'] == 'image':
                        if clip['url'].startswith('http'):
                            try:
                                frame_path = download_remote_file(clip['url'], Path("assets") / f"frame_{idx}.jpg", allow_content_type="image")
                            except Exception as e:
                                st.error(f"Failed to download image clip #{idx}: {type(e).__name__}: {e}")
                                continue
                        else:
                            frame_path = Path(clip['url'])
                        if not frame_path.exists():
                            st.error(f"Image clip not found: {frame_path}")
                            continue
                        clip_obj = ImageClip(str(frame_path)).set_duration(clip['duration'])
                    else:
                        try:
                            clip_obj = VideoFileClip(str(clip['url']))
                        except Exception as e:
                            st.error(f"Failed to read video clip {clip['url']}: {type(e).__name__}: {e}")
                            continue
                        if clip['duration'] > 0:
                            clip_obj = clip_obj.subclip(0, min(clip['duration'], clip_obj.duration))
                    if clip['speed'] != 1.0:
                        clip_obj = clip_obj.fx(vfx.speedx, clip['speed'])
                    clip_obj = clip_obj.set_fps(24).crossfadein(0.3)
                    final_clips.append(clip_obj)

                if not final_clips:
                    st.error("Unable to render video: no valid clips were available.")
                    st.stop()

                final_video = concatenate_videoclips(final_clips, method="compose")
                if st.session_state.audio_path:
                    audio_file_path = Path(st.session_state.audio_path)
                    if audio_file_path.exists():
                        try:
                            audio_clip = AudioFileClip(str(audio_file_path)).set_duration(final_video.duration)
                            final_video = final_video.set_audio(audio_clip)
                        except Exception as e:
                            st.error(f"Unable to load audio for final render: {type(e).__name__}: {e}")
                    else:
                        st.warning("Audio file not found, rendering without audio.")
                final_video.write_videofile(str(output_path), fps=24, codec="libx264", audio_codec="aac")
                st.success("Rendering complete!")
                st.video(str(output_path))
                with open(output_path, "rb") as f:
                    st.download_button("Download Final Video", f, file_name=output_path.name, use_container_width=True)
