import streamlit as st
import os, requests, time
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, vfx
from duckduckgo_search import DDGS

# --- 1. SETTINGS & THEME ---
st.set_page_config(page_title="TITAN AI STUDIO", layout="wide", initial_sidebar_state="collapsed")

# Custom Capcut-style CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #2e2e2e; color: white; border: none; }
    .stButton>button:hover { background-color: #ff4b4b; border: 1px solid white; }
    [data-testid="stHeader"] { background: rgba(0,0,0,0); }
    .block-container { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# Initialize Directories
for d in ["assets", "exports"]:
    if not os.path.exists(d): os.makedirs(d)

# Initialize Session State
if 'timeline' not in st.session_state:
    st.session_state.timeline = [] # List of {url, prompt, duration}
if 'audio_path' not in st.session_state:
    st.session_state.audio_path = None

# --- 2. TOP NAVIGATION BAR ---
with st.container():
    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 2])
    col1.title("🚀 TITAN STUDIO")
    
    # Mode Switcher
    if 'mode' not in st.session_state: st.session_state.mode = "Import"
    
    if col2.button("📥 ASSETS"): st.session_state.mode = "Import"
    if col3.button("✂️ EDITOR"): st.session_state.mode = "Editor"
    if col4.button("🎞️ EXPORT"): st.session_state.mode = "Export"

st.divider()

# --- 3. WORKSPACE LOGIC ---

# --- MODE: IMPORT (The Scraper & Generator) ---
if st.session_state.mode == "Import":
    left, right = st.columns([1, 1])
    
    with left:
        st.subheader("🌐 Web Research")
        q = st.text_input("Search for industry assets...", placeholder="e.g. Luxury Real Estate NYC")
        if st.button("Scrape Web"):
            with DDGS() as ddgs:
                results = list(ddgs.images(q, max_results=6))
                for r in results:
                    st.session_state.timeline.append({"url": r['image'], "duration": 3, "prompt": q})
            st.success("Assets added to project!")

    with right:
        st.subheader("🤖 AI Generation")
        topic = st.text_input("Ad Topic", placeholder="Enter brand name...")
        if st.button("Generate Scenes"):
            prompts = [f"Cinematic {topic} exterior", f"{topic} professional interior", f"{topic} lifestyle shot"]
            for p in prompts:
                url = f"https://image.pollinations.ai/prompt/{p.replace(' ', '%20')}?width=1920&height=1080&nologo=true"
                st.session_state.timeline.append({"url": url, "duration": 5, "prompt": p})
            st.success("AI Scenes generated!")

# --- MODE: EDITOR (The Capcut Timeline) ---
elif st.session_state.mode == "Editor":
    # Preview Window
    preview_col, settings_col = st.columns([2, 1])
    
    if st.session_state.timeline:
        with preview_col:
            st.info("Previewing Last Active Clip")
            st.image(st.session_state.timeline[-1]["url"], use_container_width=True)
            
        with settings_col:
            st.subheader("Audio Sync")
            if st.button("Fetch Background Music"):
                music_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
                r = requests.get(music_url)
                with open("assets/bg.mp3", "wb") as f: f.write(r.content)
                st.session_state.audio_path = "assets/bg.mp3"
                st.audio(st.session_state.audio_path)

        # THE HORIZONTAL TIMELINE
        st.subheader("🎞️ Timeline")
        time_cols = st.columns(max(len(st.session_state.timeline), 1))
        for i, clip in enumerate(st.session_state.timeline):
            with time_cols[i]:
                st.image(clip["url"], width=150)
                st.session_state.timeline[i]["duration"] = st.number_input(f"Secs", value=5, key=f"dur_{i}", min_value=1)
                if st.button("🗑️", key=f"del_{i}"):
                    st.session_state.timeline.pop(i)
                    st.rerun()
    else:
        st.warning("Your timeline is empty. Go to ASSETS to add content.")

# --- MODE: EXPORT (Production) ---
elif st.session_state.mode == "Export":
    st.subheader("🚀 HD Production")
    if not st.session_state.timeline:
        st.error("Nothing to export!")
    else:
        if st.button("START 1080p RENDER"):
            with st.status("Rendering Final Video...") as status:
                final_clips = []
                for i, clip in enumerate(st.session_state.timeline):
                    # Download image
                    img_data = requests.get(clip["url"]).content
                    p = f"assets/frame_{i}.jpg"
                    with open(p, "wb") as f: f.write(img_data)
                    
                    # Create Video Clip
                    c = ImageClip(p).set_duration(clip["duration"])
                    c = c.set_fps(24).crossfadein(1.0)
                    final_clips.append(c)
                
                final_video = concatenate_videoclips(final_clips, method="compose")
                
                if st.session_state.audio_path:
                    audio = AudioFileClip(st.session_state.audio_path).set_duration(final_video.duration)
                    final_video = final_video.set_audio(audio)
                
                out_path = f"exports/Final_Ad_{int(time.time())}.mp4"
                final_video.write_videofile(out_path, fps=24, codec="libx264", audio_codec="aac")
                
                st.video(out_path)
                with open(out_path, "rb") as f:
                    st.download_button("💾 Download Video", f, file_name="Ad_Export.mp4")