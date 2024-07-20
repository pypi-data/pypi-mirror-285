from gtts import gTTS

import pyttsx3

def generate_cortana_narration(text, output_filename):
    """
    Creates an audio narration of the provided 'text' and stores it as 'output_filename'.
    """
    engine = pyttsx3.init()
    engine.save_to_file(text, output_filename)
    engine.runAndWait()

def generate_google_narration(text, output_filename, language = 'es'):
    """
    Creates an audio narration of the provided 'text' with the Google voice and stores it
    as 'output_filename'. This will use the provided 'language' language for the narration.
    """
    # TODO: Check valid language tag in this table (https://en.wikipedia.org/wiki/IETF_language_tag)
    # TODO: Use this library for languages (https://pypi.org/project/langcodes/)
    tts = gTTS(text, lang = language)
    tts.save(output_filename)