# ========================================================
# AGENTIC AD STUDIO: THE "TITAN" BUILD (2026)
# ========================================================

# 1. SETUP & REPAIR (Colab Critical)
import os, shutil, requests, time, random
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

print("🛠️  Agent Team: Booting Studio & Securing Permissions...")

!pip install moviepy streamlit duckduckgo-search --quiet
!apt-get update -qq && apt-get install -y imagemagick -qq > /dev/null 2>&1
!sed -i 's/rights="none" pattern="@\*"/rights="read|write" pattern="@\*"/g' /etc/ImageMagick-6/policy.xml

from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, vfx
from moviepy.config import change_settings
from duckduckgo_search import DDGS

# Create persistent session with retry strategy
def create_session_with_retries():
    session = requests.Session()
    retry_strategy = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

# FREE AUDIO LIBRARY - Curated royalty-free tracks
FREE_AUDIO_TRACKS = {
    "1": {
        "name": "🎵 SoundHelix - Uplifting Corporate",
        "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
        "duration": "23s"
    },
    "2": {
        "name": "🎶 Bensound - Corporate Piano",
        "url": "https://www.bensound.com/bensound-music/bensound-corporate.mp3",
        "duration": "15s"
    },
    "3": {
        "name": "🎼 Bensound - Happy (Upbeat)",
        "url": "https://www.bensound.com/bensound-music/bensound-happy.mp3",
        "duration": "15s"
    },
    "4": {
        "name": "🎹 Bensound - Ukulele (Relaxed)",
        "url": "https://www.bensound.com/bensound-music/bensound-ukulele.mp3",
        "duration": "16s"
    },
    "5": {
        "name": "✨ Bensound - Sunny Day (Energetic)",
        "url": "https://www.bensound.com/bensound-music/bensound-sunny.mp3",
        "duration": "19s"
    },
    "6": {
        "name": "🚀 Bensound - Sci-Fi (Modern)",
        "url": "https://www.bensound.com/bensound-music/bensound-scifi.mp3",
        "duration": "15s"
    },
    "7": {
        "name": "🎯 Incompetech - Advancing Technology",
        "url": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Advancing%20Technology.mp3",
        "duration": "120s"
    },
    "8": {
        "name": "💎 Incompetech - Elite Success",
        "url": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Elite%20Success.mp3",
        "duration": "168s"
    },
    "9": {
        "name": "🌟 Freepd - Ambient (Minimalist)",
        "url": "https://files.freepd.com/music/Ambient%20Background.mp3",
        "duration": "180s"
    },
    "10": {
        "name": "🎬 Pixabay - Corporate Success",
        "url": "https://cdn.pixabay.com/download/audio/2022/03/10/audio_0475db1ecd.mp3",
        "duration": "112s"
    },
}

def show_audio_menu():
    """Display free audio options and get user selection."""
    print("\n" + "="*60)
    print("🎵 FREE AUDIO LIBRARY - Choose Background Music")
    print("="*60)
    for key, track in FREE_AUDIO_TRACKS.items():
        print(f"{key}. {track['name']} ({track['duration']})")
    print("="*60)
    
    while True:
        choice = input("\nSelect audio (1-10) or press Enter for default [1]: ").strip()
        if choice == "":
            choice = "1"
        if choice in FREE_AUDIO_TRACKS:
            selected = FREE_AUDIO_TRACKS[choice]
            print(f"\n✓ Selected: {selected['name']}")
            return selected["url"]
        else:
            print("❌ Invalid choice. Please enter 1-10.")

change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})
ASSETS_DIR = "production_assets"
if os.path.exists(ASSETS_DIR): shutil.rmtree(ASSETS_DIR)
os.makedirs(ASSETS_DIR)

# 2. THE 5-AGENT SQUAD
class AdProductionTeam:
    def __init__(self, brand_goal):
        self.brand_goal = brand_goal
        self.context = ""
        self.scenes = []
        self.paths = []
        self.session = create_session_with_retries()
        self.request_delay = 2  # Base delay between requests (seconds)

    def agent_researcher(self):
        """AGENT 1: Web Research - Gathers real info like Gemini."""
        print(f"🔍 [Researcher]: Searching for data on {self.brand_goal}...")
        try:
            with DDGS() as ddgs:
                results = [r['body'] for r in ddgs.text(self.brand_goal, max_results=3)]
                self.context = " ".join(results)
        except: self.context = "Standard Real Estate branding."

    def agent_scriptwriter(self):
        """AGENT 2: Creative Writing - Turns research into HD scene prompts."""
        print("✍️  [Scriptwriter]: Drafting HD cinematic storyboard...")
        # Simulates professional AD logic
        self.scenes = [
            f"{self.brand_goal} luxury home exterior, golden hour, 8k, sharp focus",
            f"Interior of a modern high-end kitchen, Keller Williams style, high definition",
            f"Professional real estate agent shaking hands with happy family, cinematic lighting",
            f"{self.brand_goal} logo over a beautiful sunset city skyline, masterpiece"
        ]

    def agent_asset_scout(self):
        """AGENT 3: Visual Generation - Fetches the HD pictures."""
        print("📸 [Scout]: Fetching high-definition AI assets with rate-limit protection...")
        for i, scene in enumerate(self.scenes):
            url = f"https://image.pollinations.ai/prompt/{scene.replace(' ', '%20')}?width=1920&height=1080&nologo=true&seed={int(time.time())+i}"
            
            max_retries = 5
            retry_count = 0
            while retry_count < max_retries:
                try:
                    # Add jitter to backoff to prevent thundering herd
                    if retry_count > 0:
                        jitter = random.uniform(0, 1)
                        wait_time = (2 ** retry_count) + jitter
                        print(f"   ⏳ Retry attempt {retry_count}/{max_retries-1}, waiting {wait_time:.2f}s...")
                        time.sleep(wait_time)
                    
                    r = self.session.get(url, timeout=30)
                    
                    # Check for rate limit headers
                    if "Retry-After" in r.headers:
                        retry_after = int(r.headers.get("Retry-After", 30))
                        print(f"   ⚠️  Server requested {retry_after}s wait (Retry-After header)")
                        time.sleep(retry_after)
                        retry_count += 1
                        continue
                    
                    if r.status_code == 429:  # Too Many Requests
                        print(f"   ⚠️  Rate limited (429). Implementing exponential backoff...")
                        retry_count += 1
                        continue
                    
                    r.raise_for_status()
                    p = f"{ASSETS_DIR}/hd_frame_{i}.jpg"
                    with open(p, "wb") as f: 
                        f.write(r.content)
                    self.paths.append(p)
                    print(f"   ✓ Frame {i+1} downloaded successfully")
                    break
                    
                except requests.exceptions.Timeout:
                    print(f"   ❌ Timeout on frame {i}. Retry {retry_count + 1}/{max_retries}")
                    retry_count += 1
                except requests.exceptions.ConnectionError as e:
                    print(f"   ❌ Connection error on frame {i}: {str(e)[:50]}. Retry {retry_count + 1}/{max_retries}")
                    retry_count += 1
                except requests.exceptions.RequestException as e:
                    print(f"   ❌ Request error on frame {i}: {str(e)[:50]}. Retry {retry_count + 1}/{max_retries}")
                    retry_count += 1
            
            if retry_count >= max_retries:
                print(f"   ⚠️  Failed to fetch frame {i} after {max_retries} retries. Continuing...")
            
            # Smart delay between requests (increased if we had retries)
            delay = self.request_delay + (retry_count * 1)
            time.sleep(delay)

    def agent_sfx_engineer(self):
        """AGENT 4: Audio Engineering - Sourcing high-quality score."""
        print("🎵 [SFX Engineer]: Selecting professional background score...")
        audio_url = show_audio_menu()
        
        max_retries = 5
        retry_count = 0
        while retry_count < max_retries:
            try:
                # Add jitter to backoff
                if retry_count > 0:
                    jitter = random.uniform(0, 1)
                    wait_time = (2 ** retry_count) + jitter
                    print(f"   ⏳ Retry attempt {retry_count}/{max_retries-1}, waiting {wait_time:.2f}s...")
                    time.sleep(wait_time)
                
                r = self.session.get(audio_url, timeout=30)
                
                # Check for rate limit headers
                if "Retry-After" in r.headers:
                    retry_after = int(r.headers.get("Retry-After", 30))
                    print(f"   ⚠️  Server requested {retry_after}s wait (Retry-After header)")
                    time.sleep(retry_after)
                    retry_count += 1
                    continue
                
                if r.status_code == 429:
                    print(f"   ⚠️  Rate limited (429). Implementing exponential backoff...")
                    retry_count += 1
                    continue
                
                r.raise_for_status()
                with open(f"{ASSETS_DIR}/bg.mp3", "wb") as f: 
                    f.write(r.content)
                print("   ✓ Audio downloaded successfully")
                return AudioFileClip(f"{ASSETS_DIR}/bg.mp3")
                
            except requests.exceptions.Timeout:
                print(f"   ❌ Timeout fetching audio. Retry {retry_count + 1}/{max_retries}")
                retry_count += 1
            except requests.exceptions.ConnectionError as e:
                print(f"   ❌ Connection error: {str(e)[:50]}. Retry {retry_count + 1}/{max_retries}")
                retry_count += 1
            except requests.exceptions.RequestException as e:
                print(f"   ❌ Request error: {str(e)[:50]}. Retry {retry_count + 1}/{max_retries}")
                retry_count += 1
        
        print("⚠️  Failed to fetch audio after {max_retries} retries. Continuing without audio.")
        return None

    def agent_master_editor(self, audio):
        """AGENT 5: The "Capcut" Logic - Final Assembly."""
        print("🎞️  [Editor]: Mastering the final AD...")
        clips = [ImageClip(p).set_duration(5).fx(vfx.fadein, 1).fx(vfx.fadeout, 1).resize(lambda t: 1 + 0.02 * t) for p in self.paths]
        final = concatenate_videoclips(clips, method="compose")
        if audio is not None: 
            final = final.set_audio(audio.subclip(0, min(audio.duration, final.duration)))
        
        output = f"Professional_Ad_{int(time.time())}.mp4"
        final.write_videofile(output, fps=24, codec="libx264", bitrate="8000k")
        print(f"\n✅ SUCCESS: '{output}' is ready for your team.")

# 3. INTERACTIVE TEAM LAUNCHER
if __name__ == "__main__":
    print("\n" + "="*50)
    print("      TEAM COLLABORATION: AI AD AGENCY v2.0")
    print("="*50)
    
    brand = input("Target for Ad (e.g., 'Keller Williams Realty NYC'): ")
    if brand.strip():
        team = AdProductionTeam(brand)
        team.agent_researcher()
        team.agent_scriptwriter()
        team.agent_asset_scout()
        music = team.agent_sfx_engineer()
        team.agent_master_editor(music)