import requests

def download_file(url, output_filename):
    """
    Receives a downloadable url as 'url' and downloads that file in
    our system as 'output_filename'.
    """
    r = requests.get(url)

    with open(output_filename, 'wb') as outfile:
        outfile.write(r.content)

    return True

def download_audio(url, output_filename):
    """
    Receives a downloadable url as 'url' and downloads that audio in
    our system as 'output_filename'.
    """
    # TODO: Check formats and that it is a valid audio (and use Enums pls)
    if not output_filename.endswith('.mp3') and not output_filename.endswith('.wav') and not output_filename.endswith('.m4a'):
        output_filename = output_filename + '.mp3'

    return download_file(url, output_filename)

def download_image(url, output_filename):
    """
    Receives a downloadable url as 'url' and downloads that image in
    our system as 'output_filename'.
    """
    # TODO: Check formats and that it is a valid image (and use Enums pls)
    if not output_filename.endswith('.jpg') and not output_filename.endswith('.png') and not output_filename.endswith('.jpeg') and not output_filename.endswith('.webp') and not output_filename.endswith('.bmp'):
        output_filename = output_filename + '.jpg'

    return download_file(url, output_filename)

def download_video(url, output_filename):
    """
    Receives a downloadable url as 'url' and downloads that video in
    our system as 'output_filename'.
    """
    # TODO: Check formats and that it is a valid audio (and use Enums pls)
    if not output_filename.endswith('.mp4') and not output_filename.endswith('.mov'):
        output_filename = output_filename + '.mp4'

    return download_file(url, output_filename)