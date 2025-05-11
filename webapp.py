# webapp.py
import streamlit as st
from stt import transcribe_audio
from translate import translate_text
from tts import speak_text

import os
import tempfile
import numpy as np
import wave
import av

from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode

st.set_page_config(page_title="Voice Translator", layout="centered")
st.title("🎙️ Real-Time Voice Translator")
st.markdown("Speak or upload audio in **English**, **Hindi**, or **Kannada** — auto-detects language and translates!")

SUPPORTED_LANGS = {
    "en": "English",
    "hi": "Hindi",
    "kn": "Kannada"
}

# Select target language
target_lang = st.selectbox("🌐 Choose Target Language", options=SUPPORTED_LANGS.keys(), format_func=lambda x: SUPPORTED_LANGS[x])

# Choose input method
input_mode = st.radio("Choose Input Method", ["🎤 Microphone", "📁 Upload Audio File"])
audio_path = None

# === Microphone Mode ===
if input_mode == "🎤 Microphone":
    st.markdown("Press the button below and speak into your mic.")

    class AudioProcessor(AudioProcessorBase):
        def __init__(self):
            self.frames = []

        def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
            audio = frame.to_ndarray()
            self.frames.append(audio)
            return frame

    ctx = webrtc_streamer(
        key="mic-stream",
        mode=WebRtcMode.SENDONLY,
        audio_receiver_size=1024,
        media_stream_constraints={"video": False, "audio": True},
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        audio_processor_factory=AudioProcessor,
    )

    if (
        ctx and ctx.state and 
        hasattr(ctx.state, "audio_processor") and 
        ctx.state.audio_processor and 
        len(ctx.state.audio_processor.frames) > 0
    ):
        st.success("✅ Audio captured! Click below to process.")

        if st.button("Translate Mic Audio"):
            pcm_data = np.concatenate(ctx.state.audio_processor.frames).astype(np.int16)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                with wave.open(tmp_file.name, "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(48000)
                    wf.writeframes(pcm_data.tobytes())
                audio_path = tmp_file.name

# === File Upload Mode ===
if input_mode == "📁 Upload Audio File":
    audio_file = st.file_uploader("Upload an audio file (wav/mp3/m4a)", type=["wav", "mp3", "m4a"])
    if audio_file is not None:
        if st.button("Translate Uploaded Audio"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                tmp_file.write(audio_file.read())
                audio_path = tmp_file.name

# === Common Pipeline ===
if audio_path:
    st.info("🔍 Transcribing...")
    text, detected_lang = transcribe_audio(audio_path)
    st.success(f"🗣️ Detected Language: {SUPPORTED_LANGS.get(detected_lang, detected_lang)}")
    st.text_area("📜 Transcribed Text", text, height=100)

    if detected_lang == target_lang:
        st.warning("⚠️ Source and target language are the same.")
    else:
        st.info("🌐 Translating...")
        translated_text = translate_text(text, src_lang=detected_lang, target_lang=target_lang)
        st.success("✅ Translation Complete!")
        st.text_area("📝 Translated Text", translated_text, height=100)

        st.info("🔊 Generating Voice...")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_out:
            speak_text(translated_text, lang=target_lang, filename=tmp_out.name)
            st.audio(tmp_out.name)

    os.remove(audio_path)
