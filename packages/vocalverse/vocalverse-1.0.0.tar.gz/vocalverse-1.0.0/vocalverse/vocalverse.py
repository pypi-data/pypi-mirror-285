import argparse
import io
import logging
import sys

from googletrans import Translator
from gtts import gTTS

# Initialize the Google Translator
translator = Translator()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

for logger_name in ('googletrans', 'httpcore', 'httpx', 'urllib3', 'requests'):
    logging.getLogger(logger_name).setLevel(logging.ERROR)

# Language dictionary for convenience
language_dict = {
    'afrikaans': 'af', 'albanian': 'sq', 'amharic': 'am', 'arabic': 'ar', 'armenian': 'hy', 'azerbaijani': 'az',
    'basque': 'eu', 'belarusian': 'be', 'bengali': 'bn', 'bosnian': 'bs', 'bulgarian': 'bg', 'catalan': 'ca',
    'cebuano': 'ceb', 'chichewa': 'ny', 'chinese (simplified)': 'zh-cn', 'chinese (traditional)': 'zh-tw',
    'corsican': 'co', 'croatian': 'hr', 'czech': 'cs', 'danish': 'da', 'dutch': 'nl', 'english': 'en',
    'esperanto': 'eo',
    'estonian': 'et', 'filipino': 'tl', 'finnish': 'fi', 'french': 'fr', 'frisian': 'fy', 'galician': 'gl',
    'georgian': 'ka',
    'german': 'de', 'greek': 'el', 'gujarati': 'gu', 'haitian creole': 'ht', 'hausa': 'ha', 'hawaiian': 'haw',
    'hebrew': 'he',
    'hindi': 'hi', 'hmong': 'hmn', 'hungarian': 'hu', 'icelandic': 'is', 'igbo': 'ig', 'indonesian': 'id',
    'irish': 'ga',
    'italian': 'it', 'japanese': 'ja', 'javanese': 'jw', 'kannada': 'kn', 'kazakh': 'kk', 'khmer': 'km', 'korean': 'ko',
    'kurdish (kurmanji)': 'ku', 'kyrgyz': 'ky', 'lao': 'lo', 'latin': 'la', 'latvian': 'lv', 'lithuanian': 'lt',
    'luxembourgish': 'lb', 'macedonian': 'mk', 'malagasy': 'mg', 'malay': 'ms', 'malayalam': 'ml', 'maltese': 'mt',
    'maori': 'mi', 'marathi': 'mr', 'mongolian': 'mn', 'myanmar (burmese)': 'my', 'nepali': 'ne', 'norwegian': 'no',
    'odia': 'or', 'pashto': 'ps', 'persian': 'fa', 'polish': 'pl', 'portuguese': 'pt', 'punjabi': 'pa',
    'romanian': 'ro',
    'russian': 'ru', 'samoan': 'sm', 'scots gaelic': 'gd', 'serbian': 'sr', 'sesotho': 'st', 'shona': 'sn',
    'sindhi': 'sd',
    'sinhala': 'si', 'slovak': 'sk', 'slovenian': 'sl', 'somali': 'so', 'spanish': 'es', 'sundanese': 'su',
    'swahili': 'sw',
    'swedish': 'sv', 'tajik': 'tg', 'tamil': 'ta', 'telugu': 'te', 'thai': 'th', 'turkish': 'tr', 'ukrainian': 'uk',
    'urdu': 'ur', 'uzbek': 'uz', 'vietnamese': 'vi', 'welsh': 'cy', 'xhosa': 'xh', 'yiddish': 'yi', 'yoruba': 'yo',
    'zulu': 'zu'
}

def get_language_code(lang):
    """Get the language code from the language dictionary."""
    lang = lang.lower()
    return language_dict.get(lang, lang)


def text_to_speech(text, lang):
    """Convert text to speech and play it using pygame."""
    import pygame
    lang_code = get_language_code(lang)
    original_stdout = sys.stdout
    sys.stdout = io.StringIO()
    pygame.mixer.init()
    sys.stdout = original_stdout

    tts = gTTS(text=text, lang=lang_code)
    with io.BytesIO() as audio_file:
        tts.write_to_fp(audio_file)
        audio_file.seek(0)
        pygame.mixer.init()
        pygame.mixer.music.load(audio_file, 'mp3')
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)


def text_to_speech_file_export(text, lang, filename, audio_file_extension):
    """Convert text to speech and export it as a file."""
    lang_code = get_language_code(lang)
    tts = gTTS(text=text, lang=lang_code)
    audio_file_path = f"{filename}.{audio_file_extension}"
    tts.save(audio_file_path)
    return audio_file_path


def translate_text(text, src_lang, dest_lang):
    """Translate text from source language to destination language."""
    src_lang_code = get_language_code(src_lang)
    dest_lang_code = get_language_code(dest_lang)
    translation = translator.translate(text, src=src_lang_code, dest=dest_lang_code)
    logging.info("Translated text: %s", translation.text)
    return translation.text


def print_language_dict():
    """Print the language dictionary."""
    print("This are List of Languages supported for the toolkit\n\nLanguageName : LanguageCode\n")
    for language, code in language_dict.items():
        print(f"{language} : {code}")


def main():
    parser = argparse.ArgumentParser(
        description="""LangStream: Text Translation, Speech Synthesis, and Audio Transcription Toolkit

        Note: During Text Translation you can utilize either language_name or language_code (Both are Case Insensitive)

        For example: 'english' or 'en' is valid input during text-translation"""
    )
    parser.add_argument('--translate', nargs=3, metavar=('TEXT', 'SRC_LANG', 'DEST_LANG'),
                        help="Translate text from source language to destination language.")
    parser.add_argument('--tts', nargs=2, metavar=('TEXT', 'LANG'), help="Convert text to speech and play it.")
    parser.add_argument('--tts-file', nargs=4, metavar=('TEXT', 'LANG', 'FILENAME', 'EXT'),
                        help="Convert text to speech and save it to a file.")
    parser.add_argument('--lang-dict', action='store_true', help="Display all supported language dictionary.")

    args = parser.parse_args()

    if args.lang_dict:
        print_language_dict()
    if args.translate:
        text, src_lang, dest_lang = args.translate
        translate_text(text, src_lang, dest_lang)
    if args.tts:
        text, lang = args.tts
        text_to_speech(text, lang)
    if args.tts_file:
        text, lang, filename, ext = args.tts_file
        logging.info(f"Audio file saved at : {text_to_speech_file_export(text, lang, filename, ext)}")


if __name__ == '__main__':
    main()
