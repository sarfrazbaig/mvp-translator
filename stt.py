from faster_whisper import WhisperModel

def transcribe_audio(audio_path):
    # Force compute on CPU by using int8 mode
    model = WhisperModel("tiny", compute_type="int8", device="cpu")

    segments, info = model.transcribe(audio_path)

    full_text = ""
    for segment in segments:
        full_text += segment.text + " "
    
    print(f"[STT] Detected Language: {info.language}")
    print(f"[STT] Transcription: {full_text.strip()}")

    return full_text.strip(), info.language