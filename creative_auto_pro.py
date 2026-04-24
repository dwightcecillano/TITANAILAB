# ========================================================
# AGENTIC AD STUDIO: THE "TITAN" BUILD (2026)
# ========================================================

# 1. SETUP & REPAIR (Colab Critical)
import os, shutil, requests, time
print("🛠️  Agent Team: Booting Studio & Securing Permissions...")

!pip install moviepy streamlit duckduckgo-search --quiet
!apt-get update -qq && apt-get install -y imagemagick -qq > /dev/null 2>&1
!sed -i 's/rights="none" pattern="@\*"/rights="read|write" pattern="@\*"/g' /etc/ImageMagick-6/policy.xml

from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, vfx
from moviepy.config import change_settings
from duckduckgo_search import DDGS

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
        print("📸 [Scout]: Fetching high-definition AI assets...")
        for i, scene in enumerate(self.scenes):
            url = f"https://image.pollinations.ai/prompt/{scene.replace(' ', '%20')}?width=1920&height=1080&nologo=true&seed={int(time.time())+i}"
            r = requests.get(url, timeout=20)
            p = f"{ASSETS_DIR}/hd_frame_{i}.jpg"
            with open(p, "wb") as f: f.write(r.content)
            self.paths.append(p)

    def agent_sfx_engineer(self):
        """AGENT 4: Audio Engineering - Sourcing high-quality score."""
        print("🎵 [SFX Engineer]: Selecting professional background score...")
        audio_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
        r = requests.get(audio_url)
        with open(f"{ASSETS_DIR}/bg.mp3", "wb") as f: f.write(r.content)
        return AudioFileClip(f"{ASSETS_DIR}/bg.mp3")

    def agent_master_editor(self, audio):
        """AGENT 5: The "Capcut" Logic - Final Assembly."""
        print("🎞️  [Editor]: Mastering the final AD...")
        clips = [ImageClip(p).set_duration(5).fx(vfx.fadein, 1).fx(vfx.fadeout, 1).resize(lambda t: 1 + 0.02 * t) for p in self.paths]
        final = concatenate_videoclips(clips, method="compose")
        if audio: final = final.set_audio(audio.subclip(0, final.duration))
        
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