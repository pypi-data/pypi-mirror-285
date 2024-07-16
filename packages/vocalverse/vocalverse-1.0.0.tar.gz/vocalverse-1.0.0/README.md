# Vocalverse


This project provides functionalities for Text Translation, Speech Synthesis, and Audio Transcription service.

## Features

Version - 1.0.0

- Translate text between different languages.
- Convert text to speech and play it.
- Convert text to speech and export it as an audio file.

## Installation

### First way : 

   ```bash 
   pip install vocalverse
   ```
if you are getting pip not found error try with pip3 (Latest Python Version 3+)

   ```bash 
   pip3 install vocalverse
   ```

### Second way : 

1. Clone the repository:

    ```bash
    git clone https://github.com/Vamshi0104/vocalverse.git
    ```

2. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Following are some example for Vocalverse CLI usage:

- [x] _**Explore all the Vocalverse capabilities**_

    ```bash
    python3 vocalverse.py --help
    ```

1. 

    ```bash
    python3 vocalverse.py --translate "Hello" "en" "tamil"
    ```

2. 

    ```bash
    python3 vocalverse.py --tts "How are you??" "en"
    ```

3. 

    ```bash
    python3 vocalverse.py --tts-file "How are you??" "en" "my_speech" "mp3"
    ```

4. 

    ```bash
    python3 vocalverse.py --lang-dict
    ```
   
### Note :
Here, 
#### -- translate for translating text to desired destination language from source language specified
#### --tts stands for text to speech
#### --tts-file stands for text to speech and export to a file



### These are List of Languages supported for the toolkit

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


### Following are some example for Vocalverse Python Function usage:

* ### Import vocalverse package 
> import vocalverse

* ### Calling this function - translates text to desired destination language from source language specified
> translate_text(text, src_lang, dest_lang)

* ### Calling this function - converts text to speech given a destination language specified
> text_to_speech(text, lang)

* ### Calling this function - converts text to speech given a destination language and exports audio to a filename and audio extension specified
> text_to_speech_file_export(text, lang, filename, audio_file_extension)

---

### _Stay tuned for more updates!! In progress: adding more functionalities to Vocalverse (in upcoming versions)_ 😊
