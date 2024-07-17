
# myutils/__init__.py

import pandas as pd
from io import BytesIO
import base64
from PIL import Image
from typing import List, Union
from .timer import *

def get_thumbnail(path):
    """
    Generate a thumbnail of an image.

    Parameters:
    path (str): The file path to the image.

    Returns:
    PIL.Image: The thumbnail image.
    """
    i = Image.open(path)
    i.thumbnail((150, 150), Image.LANCZOS)
    return i

def image_base64(im):
    """
    Convert an image to a base64 string.

    Parameters:
    im (str or PIL.Image): The image or the path to the image.

    Returns:
    str: Base64 encoded string of the image.
    """
    if isinstance(im, str):
        im = get_thumbnail(im)
    with BytesIO() as buffer:
        im.save(buffer, 'jpeg')
        return base64.b64encode(buffer.getvalue()).decode()

def image_formatter(im):
    """
    Format an image for HTML display.

    Parameters:
    im (str or PIL.Image): The image or the path to the image.

    Returns:
    str: HTML string for displaying the image.
    """
    return f'<img src="data:image/jpeg;base64,{image_base64(im)}">'

def imglist_formatter(imglist):
    """
    Format a list of images for HTML display.

    Parameters:
    imglist (list): List of images or paths to images.

    Returns:
    str: HTML string for displaying the images.
    """
    if imglist[0] is None:
        return ""
    return " ".join([f'<img src="data:image/jpeg;base64,{image_base64(im)}">' for im in imglist])

def show_pd(df, image_key: Union[str, List[str]]='image', imagelist_key: Union[str, List[str]]='masks'):
    """
    Display a pandas DataFrame with formatted image columns in Jupyter Notebook.

    Parameters:
    df (pandas.DataFrame): The DataFrame to display.
    image_key (str): The key of the column containing the image. Can be path or list of paths.
    imagelist_key (str): The key of the column containing the list of images. Can be path or list of paths.

    Returns:
    IPython.core.display.HTML: The HTML representation of the DataFrame.
    """
    from IPython.display import display, HTML
    if isinstance(image_key, str):
        image_key = [image_key]
    if isinstance(imagelist_key, str):
        imagelist_key = [imagelist_key]
    return HTML(df.to_html(formatters={**{img_key: image_formatter for img_key in image_key},
                                        **{imglist_key: imglist_formatter for imglist_key in imagelist_key}},
                           escape=False))
