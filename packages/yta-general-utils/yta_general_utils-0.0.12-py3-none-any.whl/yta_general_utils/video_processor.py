from moviepy.editor import VideoFileClip
from math import floor
from dotenv import load_dotenv

load_dotenv()

WIP_FOLDER = os.getenv('WIP_FOLDER')

import os

def get_video_duration(video_filename):
    """
    Returns the video duration of the provided video file.
    """
    return VideoFileClip(video_filename).duration 

def rescale_video(origin_filename, output_width = 1920, output_height = 1080, output_filename = 'scaled.mp4'):
    """
    This method was created to rescale videos upper to 1920x1080 or 1080x1920. This is,
    when a 4k video appears, we simplify it to 1080p resolution to work with only that
    resolution.

    This method is used in the script-guided video generation. Please, do not touch =).
    """
    # We only want to accept 16/9 or 9/16 by now, so:
    if not (output_width == 1920 and output_height == 1080) and not (output_width == 1080 and output_height == 1920):
        print('Sorry, not valid input parameters.')
        return
    
    SCALE_WIDTH = 16
    SCALE_HEIGHT = 9
    if output_width == 1080 and output_height == 1920:
        SCALE_WIDTH = 9
        SCALE_HEIGHT = 16

    clip = VideoFileClip(origin_filename)

    width = clip.w
    height = clip.h

    # We avoid things like 1927 instead of 1920
    new_width = width - width % SCALE_WIDTH
    new_height = height - height % SCALE_HEIGHT

    proportion = new_width / new_height

    if proportion > (SCALE_WIDTH / SCALE_HEIGHT):
        print('This video has more width than expected. Cropping horizontally.')
        while (new_width / new_height) != (SCALE_WIDTH / SCALE_HEIGHT):
            new_width -= SCALE_WIDTH
    elif proportion < (SCALE_WIDTH / SCALE_HEIGHT):
        print('This video has more height than expected. Cropping vertically.')
        while (new_width / new_height) != (SCALE_WIDTH / SCALE_HEIGHT):
            new_height -= SCALE_HEIGHT

    print('Final: W' + str(new_width) + ' H' + str(new_height))
    clip2 = clip.crop(x_center = floor(width / 2), y_center = floor(height / 2), width = new_width, height = new_height)
    
    # Force output dimensions
    if new_width != output_width:
        print('Forcing W' + str(output_width) + ' H' + str(output_height))
        clip2 = clip2.resize(width = output_width, height = output_height)

    # This fixes the problem of rewriting over an existing video
    clip2.write_videofile(WIP_FOLDER + 'scaled.mp4', codec = 'libx264', audio_codec = 'aac', temp_audiofile = WIP_FOLDER + 'temp-audio.m4a', remove_temp = True)
    os.remove(origin_filename)
    os.rename(WIP_FOLDER + 'scaled.mp4', output_filename)
    
    return True


def extract_audio_from_video(original_filename, output_filename):
    """
    Extracts the audio from the provided 'original_filename' and stores it as the
    'output_filename' audio file.
    """
    VideoFileClip(original_filename).audio.write_audiofile(output_filename)

def detect_scenes(video_filename):
    """
    This method detects the different scenes that are in the provided 'video_filename'
    and returns an array containing 'start' and 'end' elements. Each of those contains
    a 'second' and 'frame' field.

    TODO: This link https://www.scenedetect.com/docs/latest/api.html#example says that
    there is a backend 'VideoStreamMoviePy' class to process it with moviepy. This is
    interesting to use in a clip, and not in a filename.
    """
    # This comes from here: https://www.scenedetect.com/
    # Other project: https://github.com/slhck/scenecut-extractor (only ffmpeg)
    from scenedetect import SceneManager, open_video, ContentDetector

    video = open_video(video_filename, backend = 'moviepy')
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold = 20))  # 27 is recommended
    scene_manager.detect_scenes(video)

    scenes = []
    for scene in scene_manager.get_scene_list():
        scenes.append({
            'start': {
                'second': scene[0].get_seconds(),
                'frame': scene[0].get_frames()
            },
            'end': {
                'second': scene[1].get_seconds(),
                'frame': scene[1].get_frames()
            }
        })

    return scenes
    
    
    
    
    # This code below is working but it is quite old
    
    from scenedetect import VideoManager, SceneManager, StatsManager
    from scenedetect.detectors import ContentDetector
    from scenedetect.scene_manager import save_images, write_scene_list_html

    video_manager = VideoManager([video_filename])
    stats_manager = StatsManager()
    scene_manager = SceneManager(stats_manager)

    scene_manager.add_detector(ContentDetector(threshold = 30))
    video_manager.set_downscale_factor()

    video_manager.start()
    scene_manager.detect_scenes(frame_source = video_manager)

    scenes = scene_manager.get_scene_list()
    print(f'{len(scenes)} scenes detected!')

    save_images(
        scenes,
        video_manager,
        num_images = 1,
        image_name_template = '$SCENE_NUMBER',
        output_dir = 'scenes')

    for scene in scenes:
        start, end = scene

        # your code
        print(f'{start.get_seconds()} - {end.get_seconds()}')

    return scenes


# This is to work with abruptness and sooness (https://moviepy.readthedocs.io/en/latest/ref/videofx/moviepy.video.fx.all.accel_decel.html)
    
# I previously had 4.4.2 decorator for moviepy. I forced 4.0.2 and it is apparently working


"""
Interesting:
- https://www.youtube.com/watch?v=Ex1kuxe6jRg (el canal entero tiene buena pinta)
- https://www.youtube.com/watch?v=m6chqKlhpPo Echarle un vistazo a ese tutorial
- https://zulko.github.io/moviepy/ref/videofx.html
- https://stackoverflow.com/questions/48491070/how-to-flip-an-mp4-video-horizontally-in-python
"""

