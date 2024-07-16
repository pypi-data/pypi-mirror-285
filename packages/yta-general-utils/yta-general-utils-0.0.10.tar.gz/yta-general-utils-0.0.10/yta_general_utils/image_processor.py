from .tmp_processor import create_tmp_filename
from PIL import Image
from subprocess import run

import numpy as np
import skimage.exposure
import cv2

def resize_scaling(image_filename, width, height, output_filename = None):
    """
    Resizes the provided 'image_filename' to the provided 'width' and 'height' keeping the
    aspect ratio. This method enlarges the image to fit the desired size and then makes a 
    crop to obtain that size from the center of the resized image. If 'output_filename' is
    provided, the image is saved locally with that name.
    """
    image = Image.open(image_filename)
    image_width, image_height = image.size

    if image_width == width and image_height == height:
        return image.save(output_filename)

    aspect_ratio = image_width / image_height
    if aspect_ratio > (width / height):
        # Image is very horizontal, so width changes faster, we need to focus on height
        factor = (height * 100 / image_height) / 100
        image_width = int(image_width * factor)
        image_height = height
    else:
        # Image is very vertical, so height changes faster, we need to focus on width
        factor = (width * 100 / image_width) / 100
        image_width = 1920
        image_height = int(image_height * factor)
    image = image.resize((image_width, image_height))

    # We will crop form the center to edges
    left = 0
    right = width
    top = 0
    bottom = height
    if image_width > width:
        # If it is 1960 => leave [0, 20], get [20, 1940], leave [1940, 1960]
        margin = int((image_width - width) / 2)
        left = 0 + margin
        right = image_width - margin
        # We make and adjustment if some pixel left
        while (right - left) > width:
            right -= 1
        while (right - left) < width:
            if left > 0:
                left -= 1
            else:
                right += 1
    if image_height > height:
        # If it is 1140 => leave [0, 30], get [30, 1110], leave [1110, 1140]
        margin = int((image_height - height) / 2)
        top = 0 + margin
        bottom = image_height - margin
        # We make and adjustment if some pixel left
        while (bottom - top) > height:
            bottom -= 1
        while (bottom - top) < height:
            if top > 0:
                top -= 1
            else:
                bottom += 1

    image = image.crop((left, top, right, bottom))
    # Image that is 1920x1080 and is the center of the original image
    if output_filename:
        image.save(output_filename)

    return image

def resize_without_scaling(image_filename, width = 1920, height = 1080):
    """
    This method gets an image, resizes it and overwrites the original one.

    TODO: This method need work.
    """
    # TODO: We resize it simply, we don't care about scale
    image = cv2.imread(image_filename)
    resized_image = cv2.resize(image, dsize = (width, height), interpolation = cv2.INTER_CUBIC)
    cv2.imwrite(image_filename, resized_image)

def rgb_to_hex(r, g, b):
    """
    Returns the provided RGB color as a hex color.
    """
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)

def get_green_screen_position(image_filename):
    """
    Detects the green screen color of the provided 'image_filename' and then looks for
    the upper left corner and the bottom right corner.

    This method return an object containing 'ulx', 'uly', 'drx', 'dry' coords. It also
    returns the 'rgb_color' most common green color as an (r, g, b).

    This will return None in ['rgb_color'] field if no green color detected.
    """
    green_rgb_color = get_most_common_rgb_color(image_filename)

    image = Image.open(image_filename).convert('RGB')

    upper_left = {
        'x': 99999,
        'y': 99999,
    }
    down_right = {
        'x': -1,
        'y': -1,
    }

    for x in range(image.width):
        for y in range(image.height):
            rgb_color = (r, g, b) = image.getpixel((x, y))

            if rgb_color == green_rgb_color:
                if x < upper_left['x']:
                    upper_left['x'] = x
                if y < upper_left['y']:
                    upper_left['y'] = y
                
                """
                if x <= upper_left['x'] and y <= upper_left['y']:
                    upper_left = {
                        'x': x,
                        'y': y,
                    }
                """

                if x > down_right['x']:
                    down_right['x'] = x
                if y > down_right['y']:
                    down_right['y'] = y

                """
                if x >= down_right['x'] and y >= down_right['y']:
                    down_right = {
                        'x': x,
                        'y': y,
                    }
                """

    # We apply some margin to make sure we fit the green screen
    MARGIN = 2

    if (upper_left['x'] - MARGIN) > 0:
        upper_left['x'] -= MARGIN
    else:
        upper_left['x'] = 0

    if (upper_left['y'] - MARGIN) > 0:
        upper_left['y'] -= MARGIN
    else:
        upper_left['y'] = 0

    if (down_right['x'] + MARGIN) < 1920:
        down_right['x'] += MARGIN
    else:
        down_right['x'] = 1920

    if (down_right['y'] + MARGIN) < 1080:
        down_right['y'] += MARGIN
    else:
        down_right['y'] = 1080

    return {
        'rgb_color': green_rgb_color,
        'ulx': upper_left['x'],
        'uly': upper_left['y'],
        'drx': down_right['x'],
        'dry': down_right['y'],
    }

def get_most_common_rgb_color(image_filename, force_green = True):
    """
    Returns the most common green rgb color that exist in the provided
    'image_filename'. There could be no green color so it will return
    None, or the green color as (r, g, b) if existing.
    """
    colors = {}
    image = Image.open(image_filename).convert('RGB')

    # We will check the most common rgb color (should be the green of mask)
    for x in range(image.width):
        for y in range(image.height):
            rgb_color = (r, g, b) = image.getpixel((x, y))

            if not rgb_color in colors:
                colors[rgb_color] = 1
            else:
                colors[rgb_color] += 1

    # Check which one is the most common
    most_used_rgb_color = {
        'color': None,
        'times': 0,
    }
    for key, value in colors.items():
        if force_green:
            # We only care about green colors
            r, g, b = key
            is_green = (r >= 0 and r <= 100) and (g >= 100 and g <= 255) and (b >= 0 and b <= 100)
            if is_green:
                if value > most_used_rgb_color['times']:
                    most_used_rgb_color = {
                        'color': key,
                        'times': value
                    }
        else:
            if value > most_used_rgb_color['times']:
                most_used_rgb_color = {
                    'color': key,
                    'times': value
                }

    return most_used_rgb_color['color']

def is_valid(image_filename):
    """
    Tries to open the 'image_filename' provided to check if it is corrupt or it is valid. It 
    returns True if the provided image is valid, or False if is corrupt.
    """
    try:
        im = Image.open(image_filename)
        im.verify()
        im.close()
    except (IOError, OSError, Image.DecompressionBombError) as e:
        return False
    return True

def remove_background(image_filename, output_filename):
    """
    Removes the background of the provided 'image_filename' by using the 
    'backgroundremover' open library that is included in a comment.
    """
    # It uses (https://github.com/nadermx/backgroundremover?referral=top-free-background-removal-tools-apis-and-open-source-models)
    # That uses U2Net (https://medium.com/axinc-ai/u2net-a-machine-learning-model-that-performs-object-cropping-in-a-single-shot-48adfc158483)
    command_parameters = ['backgroundremover', '-i', image_filename, '-o', output_filename]

    run(command_parameters)

    # TODO: This below seems to work (as shown in this 
    # commit https://github.com/nadermx/backgroundremover/commit/c590858de4c7e75805af9b8ecdd22baf03a1368f)
    """
    from backgroundremover.bg import remove
    def remove_bg(src_img_path, out_img_path):
        model_choices = ["u2net", "u2net_human_seg", "u2netp"]
        f = open(src_img_path, "rb")
        data = f.read()
        img = remove(data, model_name=model_choices[0],
                    alpha_matting=True,
                    alpha_matting_foreground_threshold=240,
                    alpha_matting_background_threshold=10,
                    alpha_matting_erode_structure_size=10,
                    alpha_matting_base_size=1000)
        f.close()
        f = open(out_img_path, "wb")
        f.write(img)
        f.close()
    """

def remove_background_video(video_filename, output_filename):
    # TODO: Move to 'video_utils'
    # TODO: This is too demanding as I cannot process it properly
    # Output must end in .mov to preserve transparency
    command_parameters = ['backgroundremover', '-i', video_filename, '-tv', '-o', output_filename]

    run(command_parameters)

def remove_green_screen(image_filename, output_filename):
    # From https://stackoverflow.com/a/72280828
    # load image
    img = cv2.imread(image_filename)

    # convert to LAB
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)

    # extract A channel
    A = lab[:,:,1]

    # threshold A channel
    thresh = cv2.threshold(A, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # blur threshold image
    blur = cv2.GaussianBlur(thresh, (0,0), sigmaX = 5, sigmaY = 5, borderType = cv2.BORDER_DEFAULT)

    # stretch so that 255 -> 255 and 127.5 -> 0
    mask = skimage.exposure.rescale_intensity(blur, in_range = (127.5, 255), out_range = (0, 255)).astype(np.uint8)

    # add mask to image as alpha channel
    result = img.copy()
    result = cv2.cvtColor(img,cv2.COLOR_BGR2BGRA)
    result[:,:,3] = mask

    # save output
    cv2.imwrite(output_filename, result)

def pixelate(image_filename, i_size, output_filename):
    """
    Pixelates the provided 'image_filename' and saves it as the 'output_filename'.
    The 'i_size' is the pixelating square. The smaller it is, the less pixelated 
    its.

    'i_size' must be a tuple such as (8, 8) or (16, 16).
    """
    #read file
    img = Image.open(image_filename)

    # convert to small image
    small_img = img.resize(i_size,Image.BILINEAR)

    # resize to output size
    res = small_img.resize(img.size, Image.NEAREST)

    res.save(output_filename)

def has_transparency(image: Image):
    """
    Checks if the provided image (read with pillow) has transparency.
    """
    if image.info.get("transparency", None) is not None:
        return True
    if image.mode == "P":
        transparent = image.info.get("transparency", -1)
        for _, index in image.getcolors():
            if index == transparent:
                return True
    elif image.mode == "RGBA":
        extrema = image.getextrema()
        if extrema[3][0] < 255:
            return True

    return False

def to_sticker(image_filename, output_filename = None):
    """
    Receives an image and turns it into an sticker. This method will remove the 
    background of the provided 'image_filename' and surrounds the main object
    in that picture with a wide white border (as social networks stickers). It 
    will also crop the image to fit the remaining object only.
    """
    # From here: https://withoutbg.com/resources/creating-sticker
    # We enlarge the image 40 pixels (each border) to ensure sticker works well
    # TODO: Move this to a custom method
    enlarged_filename = create_tmp_filename('enlarged.png')
    old_im = Image.open(image_filename)
    old_size = old_im.size

    new_size = (old_size[0] + 80, old_size[1] + 80)
    new_im = Image.new("RGB", new_size)
    box = tuple((n - o) // 2 for n, o in zip(new_size, old_size))
    new_im.paste(old_im, box)
    new_im.save(enlarged_filename)

    # We remove the background of the new large image
    without_background_filename = create_tmp_filename('without_background.png')
    remove_background(enlarged_filename, without_background_filename)

    img = __read_image(without_background_filename)
    alpha = __extract_alpha_channel(img)
    big_contour = __get_largest_contour(alpha)
    contour_img = __draw_filled_contour_on_black_background(big_contour, alpha.shape)
    dilate = __apply_dilation(contour_img)
    canvas = np.zeros(img.shape, dtype = np.uint8)
    canvas = __apply_overlays(canvas, img, dilate)
    # The image is as larg as the original, maybe we need to crop it
    large_result_filename = create_tmp_filename('large.png')
    Image.fromarray(canvas.astype(np.uint8), mode = 'RGBA').save(large_result_filename)
    # Cropping considering non-alpha pixels as dimension to preserve
    im = cv2.imread(large_result_filename, cv2.IMREAD_UNCHANGED)
    x, y, w, h = cv2.boundingRect(im[..., 3])
    im2 = canvas[y:y+h, x:x+w, :]
    
    if output_filename: 
        cv2.imwrite(output_filename, cv2.cvtColor(im2, cv2.COLOR_RGBA2BGRA))
    else:
        return canvas.astype(np.uint8)

def __read_image(img_path):
    img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    return cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)

def __extract_alpha_channel(img):
    return img[:, :, 3]

def __get_largest_contour(alpha_channel):
    # Smoothing using GaussianBlur
    smoothed = cv2.GaussianBlur(alpha_channel, (15, 15), 0)
    contours_smoothed = cv2.findContours(smoothed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_smoothed = contours_smoothed[0] if len(contours_smoothed) == 2 else contours_smoothed[1]
    big_contour_smoothed = max(contours_smoothed, key = cv2.contourArea)

    # Use the smoothed contour
    peri = cv2.arcLength(big_contour_smoothed, True)
    return cv2.approxPolyDP(big_contour_smoothed, 0.001 * peri, True)

def __draw_filled_contour_on_black_background(big_contour, shape):
    contour_img = np.zeros(shape)
    cv2.drawContours(contour_img, [big_contour], 0, 255, -1)
    return contour_img

def __apply_dilation(img):
    # TODO: This is missing in source (https://withoutbg.com/resources/creating-sticker)
    # (5, 5)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (30, 30))
    return cv2.morphologyEx(img, cv2.MORPH_DILATE, kernel)

def __apply_overlays(canvas, img, dilate):
    alpha = np.expand_dims(img[:, :, 3], 2)
    alpha = np.repeat(alpha, 3, 2)
    alpha = alpha / 255

    canvas[dilate == 255] = (255, 255, 255, 255)
    canvas[:, :, 0:3] = canvas[:, :, 0:3] * (1 - alpha) + alpha * img[:, :, 0:3]

    return canvas