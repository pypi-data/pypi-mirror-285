
from yta_general_utils.text_processor import remove_non_ascii_characters
from yta_general_utils.file_downloader import download_audio
from elevenlabs import generate, save, set_api_key
from dotenv import load_dotenv
import os
import requests
import base64

load_dotenv()

API_KEY = os.getenv('ELEVENLABS_API_KEY')

# TODO: Implement a method to get an existing voice attending to a 'type' (terror, inspirational, etc.)

def generate_elevenlabs_narration(text, voice, output_filename):
    """
    Receives a 'text' and generates a single audio file with that 'text' narrated with
    the provided 'voice', stored locally as 'output_filename'.

    This method will split 'text' if too much longer to be able to narrate without issues
    due to external platform working process. But will lastly generate a single audio file.
    """
    texts = [text]
    # TODO: Set this limit according to voice type
    if len(text) > 999999:
        texts = []
        # TODO: Handle splitting text into subgroups to narrate and then join
        print('No subgrouping text yet')
        texts = [text]

    if len(texts) == 1:
        # Only one single file needed
        download_elevenlabs_audio(texts[0], voice, output_filename)
    else:
        for text in texts:
            # TODO: Generate single file
            print('Not implemented yet')

        # TODO: Join all generated files in only one (maybe we need some silence in between?)
            
    return output_filename

def download_elevenlabs_audio(text = 'Esto es API', voice = 'Freya', output_file = 'generated_elevenlabs.wav'):
    """
    Generates a narration in elevenlabs and downloads it as output_file audio file.
    """
    set_api_key(API_KEY)
    # TODO: Check if voice is valid
    # TODO: Check which model fits that voice.
    model = 'eleven_multilingual_v2'

    if not output_file.endswith('.wav'):
        output_file = output_file + '.wav'

    # TODO: Try to be able to call it with stability parameter
    audio = generate(
        text = text,
        voice = voice,
        model = model
    )

    save(audio, output_file)

def narrate_tts3(text, output_filename):
    """
    Aparrently not limited. Check, because it has time breaks and that stuff.
    """
    # From here: https://ttsmp3.com/
    headers = {
        'accept': '*/*',
        'accept-language': 'es-ES,es;q=0.9',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://ttsmp3.com',
        'referer': 'https://ttsmp3.com/',
        'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    }

    VOICES = ['Lupe', 'Penelope', 'Miguel']
    data = {
        'msg': text,
        'lang': 'Lupe',
        'source': 'ttsmp3',
    }

    response = requests.post('https://ttsmp3.com/makemp3_new.php', headers = headers, data = data)
    response = response.json()
    url = response['URL']
    # "https://ttsmp3.com/created_mp3/8b38a5f2d4664e98c9757eb6db93b914.mp3"
    download_audio(url, output_filename)


# TODO: Check https://github.com/qanastek/EasyTTS?tab=readme-ov-file
    
def narrate_tiktok(text, output_filename):
    """
    This is the tiktok voice.
    """
    # From here: https://gesserit.co/tiktok    
    # A project to use Tiktok API and cookie (https://github.com/Steve0929/tiktok-tts)
    # A project to use Tiktok API and session id (https://github.com/oscie57/tiktok-voice)
    # A project that is install and play (I think) https://github.com/Giooorgiooo/TikTok-Voice-TTS/blob/main/tiktokvoice.py


    headers = {
        'accept': '*/*',
        'accept-language': 'es-ES,es;q=0.9',
        'content-type': 'text/plain;charset=UTF-8',
        'origin': 'https://gesserit.co',
        'referer': 'https://gesserit.co/tiktok',
        'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    }

    # Non-English characters are not accepted by Tiktok TTS generation, so:
    text = remove_non_ascii_characters(text)

    # TODO: There a a lot of English US and more languages voices
    # These voices below are Spanish
    MEXICAN_VOICE = 'es_mx_002'
    SPANISH_VOICE = 'es_002'
    data = '{"text":"' + text + '","voice":"' + SPANISH_VOICE + '"}'

    response = requests.post('https://gesserit.co/api/tiktok-tts', headers=headers, data=data)
    response = response.json()
    base64_content = response['base64']

    if not output_filename.endswith('.mp3'):
        output_filename += '.mp3'

    try:
        content = base64.b64decode(base64_content)
        with open(output_filename,"wb") as f:
            f.write(content)
    except Exception as e:
        print(str(e))

    return output_filename
    