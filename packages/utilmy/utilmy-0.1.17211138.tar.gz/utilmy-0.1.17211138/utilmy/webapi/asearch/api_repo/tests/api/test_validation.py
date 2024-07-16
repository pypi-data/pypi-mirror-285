from dataclasses import dataclass

from src.api.validation import (
    api_imgasync_valid_params,
    api_imgasyncget_valid_params,
    api_imgsync_valid_params,
    api_validate_dict_schema,
    image_size_valid,
)
from src.utils.util_config import config_load


#######################################################################################
def test_api_imgsync_valid_params() -> None:
    cfg = config_load("config/dev/config_dev.yaml")
    image_str = "test"
    lang = ""
    try:
        api_imgsync_valid_params(cfg, image_str, lang)
    except ValueError as e:
        assert str(e) == "Invalid image data size"


def test_api_imgasync_valid_params() -> None:
    cfg = config_load("config/dev/config_dev.yaml")
    image_str = "test"
    lang = ""
    try:
        api_imgasync_valid_params(cfg, image_str, lang)
    except ValueError as e:
        assert str(e) == "Invalid image data size"


def test_api_imgasyncget_valid_params() -> None:
    cfg = config_load("config/dev/config_dev.yaml")
    jobid = "test" * 10
    try:
        api_imgasyncget_valid_params(cfg, jobid)
    except ValueError as e:
        assert str(e) == "Invalid jobid size"


#######################################################################################
def test_image_size_valid():
    img_str = "test"
    max_size_bytes = 1024 * 1024 * 1024
    assert image_size_valid(img_str, max_size_bytes) == True


def test_api_validate_dict_schema():
    @dataclass
    class User:
        name: str
        age: int

    user_dict = {"name": "John Doe", "age": 30}
    assert api_validate_dict_schema(user_dict, User) == True
