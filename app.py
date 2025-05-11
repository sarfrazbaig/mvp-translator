# app.py
from stt import transcribe_audio
from translate import translate_text
from tts import speak_text

SUPPORTED_LANGS = {
    "en": "English",
    "hi": "Hindi",
    "kn": "Kannada"
}

AUDIO_PATH = "test_audio.wav"

# Step 1: Transcribe + detect spoken language
text, detected_lang = transcribe_audio(AUDIO_PATH)
print(f"Detected spoken language: {SUPPORTED_LANGS.get(detected_lang, detected_lang)}")

# Step 2: Ask user which language to convert to
print("\nChoose a language to translate to:")
for code, name in SUPPORTED_LANGS.items():
    if code != detected_lang:
        print(f"- {name} ({code})")

target_lang = input("\nEnter language code (hi/en/kn): ").strip().lower()

# Safety check
if target_lang not in SUPPORTED_LANGS or target_lang == detected_lang:
    print("❌ Invalid or same as input language. Exiting.")
else:
    # Step 3: Translate
    translated_text = translate_text(text, src_lang=detected_lang, target_lang=target_lang)

    # Step 4: TTS
    speak_text(translated_text, lang=target_lang)
