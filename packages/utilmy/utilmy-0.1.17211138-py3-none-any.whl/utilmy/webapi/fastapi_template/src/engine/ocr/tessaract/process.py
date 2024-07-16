# -*- coding: utf-8 -*-
import fire
import pytesseract
from PIL import Image, ImageDraw, ImageFont
from PIL.Image import Image as ImageType


def extract_text_from_image(
    img: ImageType, lang: str = "eng", psm: int = 3, oem: int = 3, timeout=60
) -> str:
    """Extracts text from an image using pytesseract library.
    Args:
        img (Image): input image from which to extract text.
        lang (str, optional): language of text to extract. Defaults to "eng".
        psm (int, optional): page segmentation mode. Defaults to 3.
        oem (int, optional): OCR engine mode. Defaults to 3.
        timeout:             terminate tesseract job after a period of time

    Returns:
        str: extracted text from image.
    """
    text = pytesseract.image_to_string(
        img, lang=lang, config=f"--psm {psm} --oem {oem}", timeout=timeout
    )
    return text


def generate_test_image(
    text: str, image_size=(100, 30), font_size=24, font_path="tests/api/Arial.ttf"
):
    """Generates a simple image with text.

    Args:
    - text: text to draw on image.
    - image_size: A tuple of (width, height) for image.
    - font_size: size of font.
    - font_path: Path to font file.

    Returns:
    - An Image object with specified text drawn on it.
    """
    image = Image.new("RGB", image_size, "white")
    draw = ImageDraw.Draw(image)

    # Use a truetype font
    font = ImageFont.truetype(font_path, font_size)

    # Calculate text width and height to position it at center
    x1, y1, x2, y2 = font.getbbox(text)
    text_width, text_height = (x2 - x1, y2 - y1)

    text_x = (image_size[0] - text_width) / 2
    text_y = (image_size[1] - text_height) / 2

    # Draw text on image
    draw.text((text_x, text_y), text, fill="black", font=font)

    return image


####################################################################################
if __name__ == "__main__":
    fire.Fire()
