from datetime import datetime

import pytest
from fastapi import BackgroundTasks, HTTPException
from PIL import Image

from src.api.datamodels import imgasyncOutput, imgasyncRequest, imgsyncOutput
from src.api.process import api_imgasync_process, api_imgsync_process, image_extract_text
from src.engine.ocr.tessaract.process import extract_text_from_image, generate_test_image
from src.utils.util_base import uniqueid_create
from src.utils.util_config import config_load
from src.utils.util_image import text_to_base64_image
from src.utils.util_storage import storage_init

###################################################################################
from tests.mock_data import image_mocks

cfg_path = "config/local/config_test.yaml"
textref = "test text"


@pytest.fixture
def image_str():
    return image_mocks[textref]


@pytest.fixture
def lang():
    return "en"


@pytest.fixture
def storage():
    return None


###################################################################################
def test_api_imgsync_process():
    cfg = config_load(cfg_path)
    lang = None
    image_str = image_mocks[textref]

    ddict = api_imgsync_process(cfg, image_str=image_str, lang=lang)
    dref = imgsyncOutput(text=textref, ts=datetime.now().timestamp())
    assert ddict.text.split("\n")[0] == dref.text


def test_api_imgasync_process():
    cfg = config_load(cfg_path)
    lang = None
    image_str = image_mocks[textref]
    storage = storage_init(cfg)

    ddict = api_imgasync_process(
        cfg=cfg, image_str=image_str, background_tasks=BackgroundTasks(), lang=lang, storage=storage
    )


###################################################################################
def test_extract_text_from_image():
    """Test if OCR can correctly extract specified text from an image."""
    text_list = ["Hello", "Hello World"]

    for texti in text_list:
        image_str = text_to_base64_image(texti)
        text_new = image_extract_text(image_str)
        text_new = text_new.replace("\n", " ").strip()

        assert text_new == texti, f"Extracted text does not match input text {texti}"
