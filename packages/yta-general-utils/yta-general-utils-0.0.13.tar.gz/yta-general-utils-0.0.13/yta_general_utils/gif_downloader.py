from .file_downloader import download_image
from .tmp_processor import create_tmp_filename
from random import choice
from dotenv import load_dotenv
from os import getenv as os_getenv
import requests

load_dotenv()

GIPHY_API_KEY = os_getenv('GIPHY_API_KEY')

def download_gif(query, output_filename = None):
    """
    Downloads a random GIF from Giphy platform using our API key. This gif is downloaded
    in the provided 'output_filename' (but forced to be .webp).

    This method returns None if no gif found, or the output filename with it's been
    locally stored.

    Check this logged in: https://developers.giphy.com/dashboard/
    """
    limit = 5

    url = "http://api.giphy.com/v1/gifs/search"
    url += '?q=' + query + '&api_key=' + GIPHY_API_KEY + '&limit=' + str(limit)

    response = requests.get(url)
    response = response.json()

    if not response or len(response['data']) == 0:
        # TODO: Raise exception of no gif found
        print('No gif "' + query + '" found')
        return None
    
    if not output_filename:
        output_filename = create_tmp_filename('tmp_gif.webp')

    element = choice(response['data'])
    gif_url = 'https://i.giphy.com/' + element['id'] + '.webp'

    if not output_filename.endswith('.webp'):
        output_filename += '.webp'

    download_image(gif_url, output_filename)

    return output_filename