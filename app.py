import streamlit as st
import os, requests, time
from pathlib import Path
from moviepy.editor import ImageClip, VideoFileClip, AudioFileClip, concatenate_videoclips, vfx
from duckduckgo_search import DDGS

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
    "Bensound - Corporate Piano": "https://www.bensound.com/bensound-music/bensound-corporate.mp3",
    "Bensound - Happy (Upbeat)": "https://www.bensound.com/bensound-music/bensound-happy.mp3",
    "Bensound - Ukulele (Relaxed)": "https://www.bensound.com/bensound-music/bensound-ukulele.mp3",
    "Bensound - Sunny Day (Energetic)": "https://www.bensound.com/bensound-music/bensound-sunny.mp3",
    "Bensound - Sci-Fi (Modern)": "https://www.bensound.com/bensound-music/bensound-scifi.mp3",
    "Incompetech - Advancing Technology": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Advancing%20Technology.mp3",
    "Incompetech - Elite Success": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Elite%20Success.mp3",
    "Pixabay - Corporate Success": "https://cdn.pixabay.com/download/audio/2022/03/10/audio_0475db1ecd.mp3"
}


def scrape_web_data(query):
    results = []
    try:
        with DDGS() as ddgs:
            time.sleep(1)
            images = list(ddgs.images(query, max_results=8))
            for img in images:
                if img.get('image'):
                    results.append({
                        "url": img['image'],
                        "prompt": query,
                        "type": "scraped"
                    })
                    time.sleep(0.3)
    except Exception as e:
        st.warning(f"⚠️ Unable to fetch assets for '{query}'. Try again later. Error: {type(e).__name__}")
    return results

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
                st.session_state.ai_results.append({
                    "url": f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}?width=1920&height=1080&nologo=true",
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
                    st.experimental_rerun()

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
                    st.experimental_rerun()

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
            st.experimental_rerun()

    with info_col:
        total_duration = sum(clip['duration'] / clip['speed'] for clip in st.session_state.timeline) if st.session_state.timeline else 0
        st.metric("Clips in Timeline", len(st.session_state.timeline))
        st.metric("Total Duration", f"{total_duration:.1f}s")
        st.metric("Audio Loaded", "Yes" if st.session_state.audio_path else "No")

    if st.session_state.timeline:
        st.subheader("🎞️ Timeline Clips")
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
                with cols[2]:
                    if st.button("⬆️", key=f"move_up_{clip['id']}", use_container_width=True) and i > 0:
                        st.session_state.timeline[i-1], st.session_state.timeline[i] = st.session_state.timeline[i], st.session_state.timeline[i-1]
                        st.experimental_rerun()
                    if st.button("⬇️", key=f"move_down_{clip['id']}", use_container_width=True) and i < len(st.session_state.timeline) - 1:
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
                r = requests.get(audio_url, timeout=30)
                audio_path = Path("assets") / "bg.mp3"
                with open(audio_path, "wb") as f:
                    f.write(r.content)
                st.session_state.audio_path = str(audio_path)
                st.success("Audio loaded successfully")
            except Exception as e:
                st.error(f"Failed to load audio: {e}")
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
                            response = requests.get(clip['url'], timeout=30)
                            frame_path = Path("assets") / f"frame_{idx}.jpg"
                            with open(frame_path, "wb") as f:
                                f.write(response.content)
                        else:
                            frame_path = Path(clip['url'])
                        clip_obj = ImageClip(str(frame_path)).set_duration(clip['duration'])
                    else:
                        clip_obj = VideoFileClip(str(clip['url']))
                        if clip['duration'] > 0:
                            clip_obj = clip_obj.subclip(0, min(clip['duration'], clip_obj.duration))
                    if clip['speed'] != 1.0:
                        clip_obj = clip_obj.fx(vfx.speedx, clip['speed'])
                    clip_obj = clip_obj.set_fps(24).crossfadein(0.3)
                    final_clips.append(clip_obj)

                final_video = concatenate_videoclips(final_clips, method="compose")
                if st.session_state.audio_path:
                    audio_clip = AudioFileClip(st.session_state.audio_path).set_duration(final_video.duration)
                    final_video = final_video.set_audio(audio_clip)
                final_video.write_videofile(str(output_path), fps=24, codec="libx264", audio_codec="aac")
                st.success("Rendering complete!")
                st.video(str(output_path))
                with open(output_path, "rb") as f:
                    st.download_button("Download Final Video", f, file_name=output_path.name, use_container_width=True)
                
                final_video = concatenate_videoclips(final_clips, method="compose")
                
                if st.session_state.audio_path:
                    audio = AudioFileClip(st.session_state.audio_path).set_duration(final_video.duration)
                    final_video = final_video.set_audio(audio)
                
                out_path = f"exports/Final_Ad_{int(time.time())}.mp4"
                final_video.write_videofile(out_path, fps=24, codec="libx264", audio_codec="aac")
                
                st.video(out_path)
                with open(out_path, "rb") as f:
                    st.download_button("💾 Download Video", f, file_name="Ad_Export.mp4")