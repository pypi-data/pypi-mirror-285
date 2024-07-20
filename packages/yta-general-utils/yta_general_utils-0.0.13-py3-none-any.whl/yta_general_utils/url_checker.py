import requests

def url_is_ok(url):
    """
    Checks if the provided url is valid. It returns True if yes or
    False if not.
    """
    try:
        response = requests.head(url)

        if response.status_code == 200:
            return True
        else:
            return False
    except requests.ConnectionError as e:
        return e
    
def url_is_image(url):
    """
    Checks if the provided url is valid and is a valid image. It returns
    True if yes or False if not.
    """
    # TODO: Add more formats
    image_formats = ("image/png", "image/jpeg", "image/jpg")
    r = requests.head(url)
    if r.headers["content-type"] in image_formats:
        return True
    return False