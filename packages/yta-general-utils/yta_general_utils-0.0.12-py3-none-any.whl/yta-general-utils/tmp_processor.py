from random import randint
from dotenv import load_dotenv

import datetime
import os

load_dotenv()

WIP_FOLDER = os.getenv('WIP_FOLDER')

def create_tmp_filename(filename):
    """
    Returns a temporary file name with 'WIP_FOLDER' prefix and a timestamp suffix.
    """
    delta = (datetime.now() - datetime(1970, 1, 1))
    aux = filename.split('.')
    # TODO: Issue if no extension provided
    return WIP_FOLDER + aux[0] + '_' + str(int(delta.total_seconds())) + str(randint(0, 10000)) + '.' + aux[1]