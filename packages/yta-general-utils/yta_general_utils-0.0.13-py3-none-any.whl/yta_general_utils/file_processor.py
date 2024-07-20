from moviepy.editor import AudioFileClip, VideoFileClip
from pathlib import Path
from enum import Enum

import glob
import os
import sys

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

def file_exists(filename):
    """
    Checks if the provided 'filename' file or folder exist. It
    returns True if existing or False if not. 
    """
    filename = sanitize_filename(filename)

    return Path(filename).exists()

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

def write_file(text: str, filename: str):
    """
    Writes the provided 'text' in the 'filename' file. It replaces the previous content
    if existing.
    """
    if not text:
        return None
    
    if not filename:
        return None

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

def delete_file(filename: str):
    """
    Deletes the provided 'filename' if existing.

    # TODO: Maybe can be using other method that generally
    # delete files (?) Please, do if possible
    """
    if not filename or not is_file(filename):
        return None
    
    from os import remove as os_remove

    os_remove(filename)

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

def get_current_file_abspath(parent_levels: int = 0):
    """
    Returns the absolute path of the file that is currently
    being executed (in which the code is written). If 
    'parent_levels' provided, it will return the abspath
    to the parent folder that corresponds to the level
    requested.

    The absolute path is returned ending in '/' and has
    been sanitized.
    """
    abspath = sanitize_filename(os.path.dirname(os.path.abspath(sys.argv[0])))

    if parent_levels > 0:
        abspath = get_abspath_parent_folder(abspath, parent_levels)
    else:
        abspath += '/'

    return abspath

def get_abspath_parent_folder(abspath, levels = 1):
    """
    Iterates over the provided 'abspath' and goes to the parent
    folder that is 'levels' levels above. This method will
    return the new abspath sanitized and ended in '/'.
    """
    # TODO: Handle when 'levels' is greater than possible
    import os.path

    if levels <= 0:
        return abspath

    for i in range(levels):
        abspath = os.path.dirname(abspath)

    return sanitize_filename(abspath) + '/'

def rename_file(origin_filename: str, destination_filename: str, replace_if_existing: bool = False):
    """
    Renames the 'origin_filename' to the 'destination_filename'.
    If 'replace_if_existing' is True, it will replace the destination
    file if possible and allowed. If it is False, it will fail.
    """
    if not origin_filename:
        return None
    
    if not destination_filename:
        return None
    
    from os import rename as os_rename, replace as os_replace
    
    if replace_if_existing:
        os_replace(origin_filename, destination_filename)
    else:
        os_rename(origin_filename, destination_filename)