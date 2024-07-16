from yta_general_utils.tmp_processor import create_tmp_filename
from PIL import Image, ImageFont, ImageDraw

import os

# Interesting: http://www.leancrew.com/all-this/2013/11/transparency-with-pil/
# Also this: https://www.101computing.net/pixel-art-in-python/
# Try this to save drawing Pixel Arts: https://stackoverflow.com/questions/41319971/is-there-a-way-to-save-turtles-drawing-as-an-animated-gif
 
PROJECT_ABSOLUTE_PATH = os.getenv('PROJECT_ABSOLUTE_PATH')
TOUSE_ABSOLUTE_PATH = os.getenv('TOUSE_ABSOLUTE_PATH')
FONTS_PATH = 'C:/USERS/DANIA/APPDATA/LOCAL/MICROSOFT/WINDOWS/FONTS/'

def test_minecraftx():
    """
    Creates a custom 'Minecraft achievement unlocked' image. This is a good work to be able
    to create my own custom content (such as Tripadvisor reviews, Booking reviews, etc.).
    """
    FONT_FILENAME = FONTS_PATH + 'MINECRAFTIA-REGULAR.TTF'
    ACHIEVEMENT_UNLOCKED_BASE_FILENAME = TOUSE_ABSOLUTE_PATH + 'minecraft_resources/base.png'
    ICON_FILENAME = TOUSE_ABSOLUTE_PATH + 'minecraft_resources/corazon.png'
    img = Image.open(ACHIEVEMENT_UNLOCKED_BASE_FILENAME)
    icon = Image.open(ICON_FILENAME).resize((32, 32))
    
    # Call draw Method to add 2D graphics in an image
    editor = ImageDraw.Draw(img)
    
    # They say this: https://stackoverflow.com/questions/24085996/how-i-can-load-a-font-file-with-pil-imagefont-truetype-without-specifying-the-ab
    font = ImageFont.truetype(FONT_FILENAME, 16, encoding = "unic")
    # Add Text to an image
    editor.text((65, 8), text = '¡Logro desbloqueado!', fill = (255, 255, 255), font = font)
    editor.text((65, 28), text = 'Matar una oveja', fill = (240, 231, 72), font = font)
    img.paste(icon, (14, 15))
    
    # Display edited image
    img.show()
    
    # Pixel by piex

    # Save the edited image
    #img.save("car2.png")

    #Pixel by pixel
    """
    def newImg():
    img = Image.new('RGB', (100, 100))
    img.putpixel((30,60), (155,155,55))
    img.save('sqr.png')

    return img

    wallpaper = newImg()
    wallpaper.show()
    """
    
def test_minecraft():
    # This can turn a video into a pixel art video, amazing
    #test_pixelart('C:/Users/dania/Downloads/nico.MOV', 'test_pixelart.mp4')

    ICON_FILENAME = TOUSE_ABSOLUTE_PATH + 'minecraft_resources/fav.png'

    icon = Image.open(ICON_FILENAME)
    img = Image.new('RGB', (icon.width, icon.height))

    for x in range(img.width):
        for y in range(img.height):
            img.putpixel((x, y), (icon.getpixel((x, y))))
            img.save(create_tmp_filename('tmp_pixel_' + str(x) + '_' + str(y) + '.png'))

    # Try this to preview (?) (https://stackoverflow.com/questions/42719095/how-to-show-an-image-with-pillow-and-update-it)
    
def live_preview():
    import numpy as np
    import cv2

    def sin2d(x,y):
        """2-d sine function to plot"""
        return np.sin(x) + np.cos(y)

    def getFrame():
        """Generate next frame of simulation as numpy array"""

        # Create data on first call only
        if getFrame.z is None:
            xx, yy = np.meshgrid(np.linspace(0,2*np.pi,w), np.linspace(0,2*np.pi,h))
            getFrame.z = sin2d(xx, yy)
            getFrame.z = cv2.normalize(getFrame.z,None,alpha=0,beta=1,norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)

        # Just roll data for subsequent calls
        getFrame.z = np.roll(getFrame.z,(1,2),(0,1))
        return getFrame.z

    # Frame size
    w, h = 640, 480

    getFrame.z = None

    while True:
        # Get a numpy array to display from the simulation
        npimage=getFrame()

        cv2.imshow('image', npimage)
        cv2.waitKey(1)

