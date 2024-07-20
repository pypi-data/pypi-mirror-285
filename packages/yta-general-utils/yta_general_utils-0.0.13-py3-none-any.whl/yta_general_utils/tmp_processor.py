from random import randint
from datetime import datetime
from dotenv import load_dotenv
from .file_processor import delete_files, get_project_abspath, is_folder

import os

load_dotenv()

WIP_FOLDER = os.getenv('WIP_FOLDER')
if not WIP_FOLDER:
    # TODO: Create dir
    WIP_FOLDER = get_project_abspath() + 'yta_wip/'
    if not is_folder(WIP_FOLDER):
        os.mkdir(WIP_FOLDER)

def to_tmp_filename(filename):
    """
    Receives a 'filename' and turns it into a temporary filename that is
    returned including a random suffix datetime related.

    This method uses the current datetime and a random integer number to
    be unique.

    If you provide 'file.wav' it will return something like 
    'file_202406212425.wav'.
    """
    delta = (datetime.now() - datetime(1970, 1, 1))
    aux = filename.split('.')

    return aux[0] + '_' + str(int(delta.total_seconds())) + str(randint(0, 10000)) + '.' + aux[1]

def create_tmp_filename(filename):
    """
    Returns a temporary file name that includes the 'WIP_FOLDER'
    set in environment variable and also a random and datetime
    related suffix.

    If you provide 'file.wav' it will return something like 
    'wip/file_202406212425.wav'.
    """
    # TODO: Rename this as it uses wip and we do not mention it
    # TODO: Issue if no extension provided
    return WIP_FOLDER + to_tmp_filename(filename)

# TODO: Maybe rename this methods...
def create_custom_tmp_filename(filename):
    """
    Returns a new 'filename' that includes the 'WIP_FOLDER' but
    preserves the original name. This is for using the temporary
    folder but without any internal logic.
    """
    return WIP_FOLDER + filename

def clean_tmp_folder():
    """
    Removes all the existing files in the temporary folder. This folder is
    the one set in the environment 'WIP_FOLDER' variable.
    """
    delete_files(WIP_FOLDER)