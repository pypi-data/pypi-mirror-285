from PIL.Image import Image

from ascript.ios import system


def capture(png_filename=None, format='pillow') -> bytes | Image:
    if system.client:
        return system.client.screenshot(png_filename, format)
    return None
