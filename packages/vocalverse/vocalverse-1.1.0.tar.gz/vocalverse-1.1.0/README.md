# vocalverse


This project provides functionalities for Text Translation, Speech Synthesis, and Audio Transcription service.

---
### Features

Version - 1.0.0

- Translate text between different languages.
- Convert text to speech and play it.
- Convert text to speech and export it as an audio file.
- Transcribes audio file to text.
- Trims audio file efficiently.
---
### Installation

#### pip install : 

   ``` 
   pip install vocalverse
   ```
if you are getting pip not found error try with pip3 (Latest Python Version 3+)

   ``` 
   pip3 install vocalverse
   ```

#### git clone : 

1. Clone the repository:

    ```
    git clone https://github.com/Vamshi0104/vocalverse.git
    ```

2. Install the required packages:

    ```
    pip install -r requirements.txt
    ```
---
### Usage

**Explore all the vocalverse capabilities** :

#### Example for vocalverse CLI usage:

    python3 vocalverse.py --help

    python3 vocalverse.py --translate "Hello" "en" "tamil"
    
    python3 vocalverse.py --tts "How are you??" "en"
    
    python3 vocalverse.py --tts-file "How are you??" "en" "my_speech" "mp3"

    python3 langstream.py --audio-to-text your_file_name.mp3   

    python3 langstream.py --trim-audio source_file_name.mp3 dest_file_name.mp3 20 30  [trims audio file from 20 to 30 seconds) 

    python3 langstream.py --trim-audio source_file_name . 20 30  [in this case dest_file_name would be trimmed_source_file_name as output]
    
    python3 vocalverse.py --lang-dict

   
### Note :

    >> --translate for translating text to desired destination language from source language specified
    >> --tts stands for text to speech
    >> --tts-file for text to speech and export to a file
    >> --audio-to-text for transcribing audio to text
    >> --trim-audio for trimming audio from given start to end time efficiently

---

#### These are List of Languages supported for the toolkit : 


| Language Name         | Language Code |
|-----------------------|---------------|
| afrikaans             | af            |
| albanian              | sq            |
| amharic               | am            |
| arabic                | ar            |
| armenian              | hy            |
| azerbaijani           | az            |
| basque                | eu            |
| belarusian            | be            |
| bengali               | bn            |
| bosnian               | bs            |
| bulgarian             | bg            |
| catalan               | ca            |
| cebuano               | ceb           |
| chichewa              | ny            |
| chinese (simplified)  | zh-cn         |
| chinese (traditional) | zh-tw         |
| corsican              | co            |
| croatian              | hr            |
| czech                 | cs            |
| danish                | da            |
| dutch                 | nl            |
| english               | en            |
| esperanto             | eo            |
| estonian              | et            |
| filipino              | tl            |
| finnish               | fi            |
| french                | fr            |
| frisian               | fy            |
| galician              | gl            |
| georgian              | ka            |
| german                | de            |
| greek                 | el            |
| gujarati              | gu            |
| haitian creole        | ht            |
| hausa                 | ha            |
| hawaiian              | haw           |
| hebrew                | he            |
| hindi                 | hi            |
| hmong                 | hmn           |
| hungarian             | hu            |
| icelandic             | is            |
| igbo                  | ig            |
| indonesian            | id            |
| irish                 | ga            |
| italian               | it            |
| japanese              | ja            |
| javanese              | jw            |
| kannada               | kn            |
| kazakh                | kk            |
| khmer                 | km            |
| korean                | ko            |
| kurdish (kurmanji)    | ku            |
| kyrgyz                | ky            |
| lao                   | lo            |
| latin                 | la            |
| latvian               | lv            |
| lithuanian            | lt            |
| luxembourgish         | lb            |
| macedonian            | mk            |
| malagasy              | mg            |
| malay                 | ms            |
| malayalam             | ml            |
| maltese               | mt            |
| maori                 | mi            |
| marathi               | mr            |
| mongolian             | mn            |
| myanmar (burmese)     | my            |
| nepali                | ne            |
| norwegian             | no            |
| odia                  | or            |
| pashto                | ps            |
| persian               | fa            |
| polish                | pl            |
| portuguese            | pt            |
| punjabi               | pa            |
| romanian              | ro            |
| russian               | ru            |
| samoan                | sm            |
| scots gaelic          | gd            |
| serbian               | sr            |
| sesotho               | st            |
| shona                 | sn            |
| sindhi                | sd            |
| sinhala               | si            |
| slovak                | sk            |
| slovenian             | sl            |
| somali                | so            |
| spanish               | es            |
| sundanese             | su            |
| swahili               | sw            |
| swedish               | sv            |
| tajik                 | tg            |
| tamil                 | ta            |
| telugu                | te            |
| thai                  | th            |
| turkish               | tr            |
| ukrainian             | uk            |
| urdu                  | ur            |
| uzbek                 | uz            |
| vietnamese            | vi            |
| welsh                 | cy            |
| xhosa                 | xh            |
| yiddish               | yi            |
| yoruba                | yo            |
| zulu                  | zu            |


#### Example for vocalverse Python function usage:

* ##### Import vocalverse package 
> import vocalverse

* ##### Calling this function - translates text to desired destination language from source language specified
> translate_text(text, src_lang, dest_lang)

* ##### Calling this function - converts text to speech given a destination language specified
> text_to_speech(text, lang)

* ##### Calling this function - converts text to speech given a destination language and exports audio to a filename and audio extension specified
> text_to_speech_file_export(text, lang, filename, audio_file_extension)

* ##### Calling this function - transcribes audio file to text specified audio_file_name in input
> audio_to_text(audio_filename)

* ##### Calling this function - trims audio file from specified start to end time(in seconds) [Note : dest_audio_filename can be '.' - to name it as trimmed_src_audio_filename]
> trim_audio(src_audio_filename, dest_audio_filename, start_time, end_time)
---

##### >>> _Stay tuned for more updates from vocalverse!!!_