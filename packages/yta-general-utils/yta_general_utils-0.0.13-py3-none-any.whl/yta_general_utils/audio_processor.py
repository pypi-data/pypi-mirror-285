from moviepy.editor import AudioFileClip, CompositeAudioClip
from pydub import AudioSegment, silence
from df.enhance import enhance, init_df, load_audio, save_audio

import os

def crop(audio_filename, duration, output_filename):
    """
    Crops the 'audio_filename' provided to the requested 'duration'.

    This method returns the new audio 'output_filename' if valid, or
    False if it was not possible to crop it.
    """
    audio_clip = AudioFileClip(audio_filename)

    if audio_clip.duration < duration:
        print('audio is shorter than requested duration')
        return False
    
    audio_clip.set_duration(duration).write_audiofile(output_filename)

    return output_filename

def mp3_to_wav(mp3_filename, output_wav_filename):
    """
    Receives an .mp3 file 'mp3_filename' and turns it into a .wav
    file stored in 'output_wav_filename'.
    """
    # TODO: Generalize this method to swap between formats
    sound = AudioSegment.from_mp3(mp3_filename)
    sound.export(output_wav_filename, format = "wav")

def remove_noise(audio_filename, audio_output_filename):
    """
    Removes the noise from the provided 'audio_filename' and creates a new
    file 'audio_output_filename' without noise.

    TODO: This fails when .mp3 is used, so we need to transform into wav.

    TODO: Output file must be also wav
    """
    # Based on this (https://medium.com/@devesh_kumar/how-to-remove-noise-from-audio-in-less-than-10-seconds-8a1b31a5143a)
    # https://github.com/Rikorose/DeepFilterNet
    # Guide to installation is right here, in the link below:
    # https://github.com/Rikorose/DeepFilterNet?tab=readme-ov-file#deepfilternet-python-pypi
    # TODO: This is failing now saying 'File contains data in an unknon format'...
    # I don't know if maybe some library, sh*t...
    # Load default model
    TMP_WAV_FILENAME = 'tmp_wav.wav'
    if audio_filename.endswith('.mp3'):
        # TODO: Maybe it is .wav but not that format...
        mp3_to_wav(audio_filename, TMP_WAV_FILENAME)
        audio_filename = TMP_WAV_FILENAME

    model, df_state, _ = init_df()
    audio, _ = load_audio(audio_filename, sr = df_state.sr())
    # Remove the noise
    enhanced = enhance(model, df_state, audio)

    save_audio(audio_output_filename, enhanced, df_state.sr())

    try:
        os.remove(TMP_WAV_FILENAME)
    except:
        pass

def get_audio_length_in_seconds(input_file):
    """
    Returns the provided audio file 'input_file' duration in seconds.

    This method uses AudioFileClip.duration.
    
    It must be an audio file.
    """
    audiofileclip = AudioFileClip(input_file)
    
    return audiofileclip.duration

def add_audio_to_audio(audio_filename, new_audio_filename, start_time = 1.0):
    """
    We receive an audio file called 'audio_filename' and we append the provided
    'new_audio_filename' to that existing audio to sound over it. That second 
    sound will start in the 'start_time' second of the first 'audio_filename'
    """
    first_audioclip = AudioFileClip(audio_filename)
    second_audioclip = AudioFileClip(new_audio_filename)

    combined = CompositeAudioClip([first_audioclip, second_audioclip.set_start(start_time)])
    combined.fps = 44100
    
    combined.write_audiofile('audio_combined.mp3')

def detect_silences(audio_filename, silence_min_length = 250):
    """
    This method detects the silences existing in the provided 'audio_filename' that
    are of a minimum of 'silence_min_length' long. It will return an array containing
    tuples (X.XX, Y.YY) of start and end silence moments (in seconds).
    """
    audio = __get_audio_segment(audio_filename)

    dBFS = audio.dBFS
    silences = silence.detect_silence(audio, min_silence_len = silence_min_length, silence_thresh = dBFS - 16)

    # [(1.531, 1.946), (..., ...), ...] in seconds
    return [((start / 1000), (stop / 1000)) for start, stop in silences]

def __get_audio_segment(audio_filename):
    if not '.' in audio_filename:
        return None
    
    extension = audio_filename.split('.')[1]
    myaudio = AudioSegment.from_file(audio_filename)
    """
    if extension == 'mp3':
        myaudio = AudioSegment.from_mp3(audio_filename)
    elif extension == 'wav':
        myaudio = AudioSegment.from_wav(audio_filename)
    else:
        # TODO: Do this work? I think no, because it is not configured
        myaudio = AudioSegment.from_file(audio_filename)
    """

    return myaudio