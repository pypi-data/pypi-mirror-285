import base64
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont


def text_to_base64_image(
    text="Hello, World!", font_path="resource/Arial.ttf", font_size=40, image_size=(512, 512)
):
    """Generates an image with given text and saves it as a base64 encoded string.

    Args:
        text (str): text to be displayed on image. Defaults to "Hello, World!".
        font_path (str): path to font file. Defaults to "Arial.ttf".
        font_size (int): size of font. Defaults to 40.
        image_size (tuple): size of image. Defaults to (512, 512).

    Returns:
        str: base64 encoded string representing generated image.
    Usage:
        base64_image = generate_text("Sample Text")
        print(base64_image)
    """
    image = Image.new("RGB", image_size, "white")
    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype(font_path, size=font_size)

    # Calculate text width and height
    x1, y1, x2, y2 = font.getbbox(text)
    text_width, text_height = (x2 - x1, y2 - y1)

    # Calculate x,y coordinates of text
    x = (image_size[0] - text_width) / 2
    y = (image_size[1] - text_height) / 2

    # Add text to image
    draw.text((x, y), text, fill="black", font=font)

    # Save image to a bytes buffer
    img_bytes = BytesIO()
    image.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    # Encode image to base64
    img_base64 = base64.b64encode(img_bytes.read()).decode("ascii")
    return img_base64
