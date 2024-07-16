from moviepy.editor import AudioFileClip, VideoFileClip
from pathlib import Path
from enum import Enum

import glob
import os

# TODO: Maybe move this to an specific enums file?
class FILE_SEARCH_OPTION(Enum):
    FILES_AND_FOLDERS = 'fifo'
    FILES_ONLY = 'fi'
    FOLDERS_ONLY = 'fo'

# TODO: Maybe move this below to a 'file_checker.py'?
def file_has_extension(filename):
    if get_file_extension(filename):
        return True
    
    return False

def get_file_extension(filename):
    filename = get_filename(filename)

    if '.' in filename:
        aux = filename.split('.')

        return aux[len(aux) - 1]
    
    return None

def is_file(filename):
    """
    Checks if the provided 'filename' is an existing and
    valid file. It returns True if yes or False if not.
    """
    filename = sanitize_filename(filename)
    filename = Path(filename)

    return filename.exists() and filename.is_file()

def is_folder(filename):
    """
    Checks if the provided 'filename' is an existing and
    valid folder. It returns True if yes or False if not.
    """
    filename = sanitize_filename(filename)
    filename = Path(filename)

    return filename.exists() and filename.is_dir()

def exists(filename):
    """
    Checks if the provided 'filename' file or folder exist. It
    returns True if existing or False if not. 
    """
    filename = sanitize_filename(filename)

    return Path(filename).exists()

def file_exists(filename):
    """
    @deprecated
    TODO: This method should be deprecated as it is making more
    logical comparisons that it should.

    Checks if the provided 'filename' exist and is a file.
    """
    return Path(filename).is_file()

def file_is_audio_file(filename):
    """
    Checks if the provided 'filename' is an audio file by
    trying to instantiate it as a moviepy AudioFileClip.
    """
    try:
        AudioFileClip(filename)
    except:
        return False
    
    return True

def file_is_video_file(filename):
    """
    Checks if the provided 'filename' is a video file by
    trying to instantiate it as a moviepy VideoFileClip.
    """
    try:
        VideoFileClip(filename)
    except:
        return False
    
    return True
# TODO: Maybe move this above to a 'file_checker.py'?

def write_file(text, filename):
    """
    Writes the provided 'text' in the 'filename' file. It replaces the previous content
    if existing.
    """
    f = open(filename, 'w', encoding = 'utf8')
    f.write(text)
    f.close()

def delete_files(folder, pattern = '*'):
    """
    Delete all the files in the 'folder' provided that match the provided
    'pattern'. The default pattern removes all existing files, so please
    use this method carefully.
    """
    # TODO: Make some risky checkings  about removing '/', '/home', etc.
    files = list(folder, FILE_SEARCH_OPTION.FILES_ONLY, pattern)
    # TODO: Check what happens if deleting folders with files inside
    for file in files:
        os.remove(file)

def sanitize_filename(filename: str):
    """
    This method checks the provided 'filename' and turns any 
    backslash character into a '/' (slash) one, returning the
    new string.
    """
    if '\\' in filename:
        filename = filename.replace('\\', '/')

    return filename

def get_filename(filename):
    """
    This method returns the filename, avoiding the path, of
    the provided 'filename'. This method includes the extension
    if existing.
    """
    aux = sanitize_filename(filename).split('/')

    return aux[len(aux) - 1]

def list(abspath, option: FILE_SEARCH_OPTION = FILE_SEARCH_OPTION.FILES_AND_FOLDERS, pattern: str = '*', recursive: bool = False):
    """
    List what is inside the provided 'abspath'. This method will list files and
    folders, files or only folders attending to the provided 'option'. It will
    also filter the files/folders that fit the provided 'pattern' (you can use
    '*' as wildcard, so for example '*.jpg' will list all images). This method
    can also be used in a recursive way if 'recursive' parameter is True, but
    take care of memory consumption and it would take its time to perform.

    This method returns a list with all existing elements absolute paths 
    sanitized.
    """
    if not abspath:
        return None
    
    abspath = sanitize_filename(abspath)
    list = []

    # This below get files and folders
    files_and_folders = [sanitize_filename(f) for f in glob.glob(pathname = abspath + pattern, recursive = recursive)]

    if option == FILE_SEARCH_OPTION.FILES_ONLY:
        for f in files_and_folders:
            if is_file(f):
                list.append(f)
    elif option == FILE_SEARCH_OPTION.FOLDERS_ONLY:
        for f in files_and_folders:
            if is_folder(f):
                list.append(f)
    elif option == FILE_SEARCH_OPTION.FILES_AND_FOLDERS:
        list = files_and_folders
    
    return list

def get_project_abspath():
    """
    Returns the absolute path of the current project (the
    one that is being executed and using this library.

    The absolute path returned ends in '/' and has been
    sanitized.
    """
    return sanitize_filename(os.getcwd()) + '/'
