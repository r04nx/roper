from PIL import ImageGrab
import tempfile
import os

def take_screenshot():
    # Take a screenshot of the entire screen
    img = ImageGrab.grab()
    temp_dir = tempfile.gettempdir()
    img_path = os.path.join(temp_dir, 'roper_screenshot.png')
    img.save(img_path)
    return img_path 