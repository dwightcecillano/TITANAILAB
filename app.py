import streamlit as st
import os, sys, requests, time

# --- THE MOVIEPY 2.1.1 STABLE BRIDGE ---
try:
    import moviepy
    from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
    # Safe check for effects
    HAS_FX = False
    try:
        from moviepy.video.fx.fadein import fadein
        from moviepy.video.fx.fadeout import fadeout
        HAS_FX = True
    except:
        pass 
except Exception as e:
    st.error(f"Critical Engine Error: {e}")
    st.stop()

from duckduckgo_search import DDGS

# --- STUDIO SETUP ---
st.set_page_config(page_title="Titan Universal HD Studio", layout="wide")
for d in ["web_assets", "ai_assets", "exports"]:
    if not os.path.exists(d): os.makedirs(d)

# --- NAVIGATION ---
mode = st.sidebar.radio("Navigation:", ["1. Web Scraper", "2. AI Scriptwriter", "3. SFX & Audio", "4. Render & HD Export"])

if 'script' not in st.session_state:
    st.session_state.script = ["", "", "", ""]

# --- 1. WEB SCRAPER (RESILIENT VERSION) ---
if mode == "1. Web Scraper":
    st.header("🌐 Universal Web Scraper")
    st.info("Limit reached? Wait 60s or try a different search term.")
    q = st.text_input("Find assets (Logos, industry photos)...", key="scraper_input")
    
    if st.button("Scrape Assets"):
        try:
            with DDGS() as ddgs:
                # Add a tiny delay to appear more 'human' to the server
                time.sleep(1.5) 
                results = list(ddgs.images(q, max_results=4))
                
                if results:
                    cols = st.columns(2)
                    for idx, r in enumerate(results):
                        cols[idx % 2].image(r['image'], use_container_width=True)
                else:
                    st.warning("No results. Try a broader search (e.g., 'Modern House' instead of a specific address).")
        except Exception as e:
            if "403" in str(e) or "Ratelimit" in str(e):
                st.error("⏳ DuckDuckGo is on timeout. Please wait a minute or use the AI Scriptwriter tab to generate images instead.")
            else:
                st.error(f"Error: {e}")

# --- 2. AI SCRIPTWRITER ---
elif mode == "2. AI Scriptwriter":
    st.header("✍️ AI Scriptwriter")
    topic = st.text_input("Ad Topic")
    if st.button("Generate"):
        st.session_state.script = [f"Cinematic wide shot of {topic}, 8k", f"Close up of {topic}", f"Person using {topic}", f"{topic} branding"]
    for i in range(4):
        st.session_state.script[i] = st.text_area(f"Scene {i+1}", st.session_state.script[i])

# --- 3. SFX & AUDIO ---
elif mode == "3. SFX & Audio":
    st.header("🎵 Audio Engine")
    if st.button("Sync Audio"):
        url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
        with open("web_assets/audio.mp3", "wb") as f: f.write(requests.get(url).content)
        st.audio(url)

# --- 4. RENDER & HD EXPORT ---
elif mode == "4. Render & HD Export":
    st.header("🎞️ HD Production")
    if st.button("🚀 EXECUTE 1080p RENDER"):
        clips = []
        with st.status("Producing HD Final File...") as status:
            for i, prompt in enumerate(st.session_state.script):
                if not prompt: continue
                url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}?width=1920&height=1080&nologo=true&seed={i}"
                p = f"ai_assets/s_{i}.jpg"
                with open(p, "wb") as f: f.write(requests.get(url).content)
                
                # NATIVE v2.x SYNTAX
                c = ImageClip(p).with_duration(5)
                
                # Only apply effects if the import actually worked
                if HAS_FX:
                    try:
                        c = fadein(c, 1.0)
                        c = fadeout(c, 1.0)
                    except:
                        pass
                
                clips.append(c)

            if clips:
                final = concatenate_videoclips(clips, method="compose")
                if os.path.exists("web_assets/audio.mp3"):
                    audio = AudioFileClip("web_assets/audio.mp3").with_duration(final.duration)
                    final = final.with_audio(audio)
                
                out = f"exports/Final_{int(time.time())}.mp4"
                final.write_videofile(out, fps=24, codec="libx264", bitrate="8000k")
                st.video(out)