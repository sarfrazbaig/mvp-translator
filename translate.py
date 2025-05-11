# translate.py
from googletrans import Translator

translator = Translator()

def translate_text(text, src_lang="en", target_lang="hi"):
    translated = translator.translate(text, src=src_lang, dest=target_lang)
    print(f"[Translate] Translation: {translated.text}")
    return translated.text
