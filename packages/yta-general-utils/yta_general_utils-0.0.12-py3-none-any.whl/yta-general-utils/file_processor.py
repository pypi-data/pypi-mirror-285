from moviepy.editor import AudioFileClip, VideoFileClip
from pathlib import Path

def write_file(text, filename):
    """
    Writes the provided 'text' in the 'filename' file. It replaces the previous content
    if existing.
    """
    f = open(filename, 'w', encoding = 'utf8')
    f.write(text)
    f.close()

def file_exists(filename):
    """
    Checks if the provided 'filename' exist and is a file.
    """
    return Path(filename).is_file()

def file_is_audio_file(filename):
    try:
        AudioFileClip(filename)
    except:
        return False
    return True

def file_is_video_file(filename):
    try:
        VideoFileClip(filename)
    except:
        return False
    return True