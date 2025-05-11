# tts.py
from gtts import gTTS
import os

def speak_text(text, lang="hi", filename="translated_output.mp3"):
    tts = gTTS(text=text, lang=lang)
    tts.save(filename)
    print(f"[TTS] Audio saved as {filename}")

    # Optional: play the audio (only on Windows/macOS)
    try:
        os.system(f"start {filename}")  # Windows
    except:
        pass
