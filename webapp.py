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

from streamlit_webrtc import webrtc_streamer, AudioProcessorBase

st.set_page_config(page_title="Voice Translator", layout="centered")
st.title("🎙️ Real-Time Voice Translator")
st.markdown("Speak or upload audio in **English**, **Hindi**, or **Kannada** — we'll detect the language and translate it for you.")

SUPPORTED_LANGS = {
    "en": "English",
    "hi": "Hindi",
    "kn": "Kannada"
}

# --- Input Mode Selection ---
input_mode = st.radio("Choose Input Mode", ["🎤 Record from Microphone", "📁 Upload Audio File"])
target_lang = st.selectbox("🌐 Choose Target Language", options=SUPPORTED_LANGS.keys(), format_func=lambda x: SUPPORTED_LANGS[x])

audio_path = None

# --- Mic Input with webrtc ---
if input_mode == "🎤 Record from Microphone":
    st.markdown("Click below to start recording. Speak clearly in English, Hindi, or Kannada.")

    class AudioProcessor(AudioProcessorBase):
        def __init__(self):
            self.frames = []

        def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
            pcm = frame.to_ndarray()
            self.frames.append(pcm)
            return frame

    ctx = webrtc_streamer(
        key="mic-audio",
        mode="sendonly",
        audio_receiver_size=256,
        media_stream_constraints={"video": False, "audio": True},
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        audio_processor_factory=AudioProcessor
    )

    if ctx.state.audio_processor and len(ctx.state.audio_processor.frames) > 0:
        st.success("✅ Audio captured! Click 'Translate' to continue.")

        if st.button("Translate"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                output_path = tmp_file.name

            wf = wave.open(output_path, "wb")
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(48000)
            pcm_data = np.concatenate(ctx.state.audio_processor.frames).astype(np.int16)
            wf.writeframes(pcm_data.tobytes())
            wf.close()

            audio_path = output_path

# --- File Upload Mode ---
elif input_mode == "📁 Upload Audio File":
    audio_file = st.file_uploader("Upload an audio file (wav/mp3/m4a)", type=["wav", "mp3", "m4a"])

    if audio_file is not None and st.button("Translate"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(audio_file.read())
            audio_path = tmp_file.name

# --- Translation Pipeline ---
if audio_path:
    st.info("🔍 Transcribing...")
    text, detected_lang = transcribe_audio(audio_path)
    st.success(f"✅ Detected Language: {SUPPORTED_LANGS.get(detected_lang, detected_lang)}")
    st.text_area("📜 Transcribed Text", text, height=100)

    if detected_lang == target_lang:
        st.warning("⚠️ Source and target languages are the same. Please select a different target.")
    else:
        st.info("🌐 Translating...")
        translated_text = translate_text(text, src_lang=detected_lang, target_lang=target_lang)
        st.success("✅ Translation Complete!")
        st.text_area("📝 Translated Text", translated_text, height=100)

        st.info("🔊 Generating speech output...")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio_out:
            speak_text(translated_text, lang=target_lang, filename=tmp_audio_out.name)
            st.audio(tmp_audio_out.name)

    os.remove(audio_path)
