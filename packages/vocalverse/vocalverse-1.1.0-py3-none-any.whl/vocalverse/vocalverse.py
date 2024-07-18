import argparse
import io
import logging
import sys
import threading
import re
import time

import whisper
from googletrans import Translator
from gtts import gTTS

from pydub import AudioSegment

# Initialize the Google Translator
translator = Translator()

audio_regex_pattern = re.compile(r'\.(mp3|wav|flac|aac|ogg|m4a)$', re.IGNORECASE)

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

def is_valid_audio_file(filename):
    return bool(audio_regex_pattern.search(filename))

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

def countdown_timer(stop_event):
    """
    Prints a countdown timer every 10 seconds until the stop event is set.

    Parameters:
    stop_event (threading.Event): The event to signal the countdown to stop.
    """
    counter = 0
    while not stop_event.is_set():
        time.sleep(10)
        counter += 10
        logging.info(f"Please wait...Converting Audio to Text efficiently -- : {counter} seconds elapsed")


def audio_to_text(audio_filename: str, model_name: str = 'large') -> str:
    """
    Converts an audio file to text, extracting only lyrics with high accuracy using OpenAI's Whisper model.

    Parameters:
    audio_filename (str): The path to the audio file.
    model_name (str): The model name to be used by Whisper (default is 'base').

    Returns:
    str: The extracted text from the audio file in the recognized language.
    """
    if not audio_regex_pattern.search(audio_filename):
        logging.error(f"{audio_filename} is not an allowed audio file. Allowed file extensions: [mp3, wav, flac, aac, ogg, m4a]")
        return
    stop_event = threading.Event()
    countdown_thread = threading.Thread(target=countdown_timer, args=(stop_event,))

    try:
        # Start countdown timer thread
        countdown_thread.start()
        # Load Whisper model
        model = whisper.load_model(model_name)
        # Transcribe audio file
        logging.info(f"Transcribing audio file: {audio_filename}")
        result = model.transcribe(audio_filename)
        text = result['text']
        logging.info(f"Transcription completed\n\nTranscription Result : {text}")
        return text

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return ""

    finally:
        # Stop countdown timer thread
        stop_event.set()
        countdown_thread.join()


def trim_audio(src_audio_filename: str, dest_audio_filename: str, start_time: float, end_time: float):
    """
    Trims the audio file given specific start and end times.

    Parameters:
    audio_filename (str): The path to the input audio file.
    dest_audio_filename (str): The path to save the trimmed audio file.
    start_time (float): The start time in seconds (can include milliseconds).
    end_time (float): The end time in seconds (can include milliseconds).
    """
    if not is_valid_audio_file(src_audio_filename):
        logging.error(f"{src_audio_filename} is not an allowed audio file. Allowed file extensions: [mp3, wav, flac, aac, ogg, m4a]")
        return

    if dest_audio_filename == ".":
        dest_audio_filename = "trimmed_" + src_audio_filename

    if not is_valid_audio_file(dest_audio_filename):
        logging.error(f"{dest_audio_filename} is not an allowed audio file. Allowed file extensions: [mp3, wav, flac, aac, ogg, m4a]")
        return
    try:
        # Load audio file
        logging.info(f"Loading audio file: {src_audio_filename}")
        audio = AudioSegment.from_file(src_audio_filename)

        # Trim the audio
        start_ms = start_time * 1000  # Convert to milliseconds
        end_ms = end_time * 1000  # Convert to milliseconds
        logging.info(f"Trimming audio from {start_time} seconds to {end_time} seconds.")
        trimmed_audio = audio[start_ms:end_ms]
        # Export the trimmed audio
        trimmed_audio.export(dest_audio_filename, format="wav")
        logging.info(f"Trimmed audio saved as: {dest_audio_filename}")

    except Exception as e:
        logging.error(f"An error occurred: {e}")

def text_to_speech_file_export(text, lang, filename, audio_file_extension):
    """Convert text to speech and export it as a file."""
    lang_code = get_language_code(lang)
    tts = gTTS(text=text, lang=lang_code)
    audio_file_path = f"{filename}.{audio_file_extension}"
    tts.save(audio_file_path)
    logging.info(f"Audio file saved at : {audio_file_path}")
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
    parser.add_argument('--audio-to-text', nargs=1, metavar=('AUDIO_FILENAME'), help="Convert audio to text.")
    parser.add_argument('--trim-audio', nargs=4,metavar=('AUDIO_FILENAME', 'DEST_AUDIO_FILENAME', 'START_TIME', 'END_TIME'),help="Trim the audio file from start time to end time efficiently.")

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
        text_to_speech_file_export(text, lang, filename, ext)
    if args.audio_to_text:
        audio_filename = args.audio_to_text[0]
        audio_to_text(audio_filename)
    if args.trim_audio:
        audio_filename, dest_audio_filename, start_time, end_time = args.trim_audio
        if dest_audio_filename == ".":
            dest_audio_filename = ("trimmed_" + audio_filename)
        trim_audio(audio_filename, dest_audio_filename, float(start_time), float(end_time))


if __name__ == '__main__':
    main()
