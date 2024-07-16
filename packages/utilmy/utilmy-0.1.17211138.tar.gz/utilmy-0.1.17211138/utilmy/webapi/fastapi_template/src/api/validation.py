# -*- coding: utf-8 -*-
import base64
import json
import sys
from dataclasses import dataclass, fields
from typing import Any, Dict, Tuple, Type

from src.utils.util_log import log, loge


from fastapi import HTTPException



#######################################################################################
def api_imgsync_valid_params(
    cfg: dict,
    image_str: str,
    lang=None,
) -> None:
    """A function to validate parameters for image synchronization API.
    Args:
        cfg (dict): configuration dictionary.
        image_str (str): image data in string format.
        lang (Optional): language of image data.

    Raises:
        ValueError: If image size is invalid.

    Returns:
        None
    """
    maxsize = cfg["service"]["max_size_bytes_image"]

    # TODO: validate params
    if not image_size_valid(image_str, max_size_bytes=maxsize):
        # raise ValueError("Invalid image data size")
        raise HTTPException(status_code=400, detail= f"Invalid image data size")


def api_imgasync_valid_params(
    cfg: dict,
    image_str: str,
    lang=None,
) -> None:
    """A function to validate parameters for an asynchronous image API request.
    Args:
        cfg (dict): A dictionary containing configuration parameters.
        image_str (str): A string representing image data.
        lang (optional): An optional parameter for specifying language.

    Raises:
        ValueError: If image size is invalid.

    Returns:
        None
    """

    if not image_size_valid(image_str):
        # raise ValueError("Invalid image data size")
        raise HTTPException(status_code=400, detail= f"Invalid image data size")


def api_imgasyncget_valid_params(
    cfg: dict,
    jobid: str,
) -> None:
    """Validates parameters for `api_imgasyncget` function.
    Args:
        cfg (dict): configuration dictionary.
        jobid (str): job ID.

    Raises:
        ValueError: If jobid size is invalid or if jobid contains invalid characters.

    Returns:
        None
    """
    if len(jobid) > 36:
        # raise ValueError("Invalid jobid size")
        raise HTTPException(status_code=400, detail= "Invalid jobid size")

    if jobid.isalnum():
        # raise ValueError("Invalid jobid chars")
        raise HTTPException(status_code=400, detail= "Invalid jobid format")



#######################################################################################
def image_size_valid(img_str: str, max_size_bytes=1024 * 1024 * 1024) -> bool:
    """A function to check if size of an image encoded in base64 is within a specified maximum limit.
    Args:
        img_str (str): base64 encoded image data to be checked.
        max_size_bytes (int, optional): maximum size in bytes allowed for image. Defaults to 1024 * 1024 * 1024.

    Returns:
        bool: True if image size is within limit, False otherwise.
    """
    try:
        image_data = base64.b64decode(img_str, validate=True)
        if len(image_data) > max_size_bytes:
            loge(f"Image size exceeds maximum limit of {max_size_bytes} bytes")
            return False

    except Exception as e:
        loge(f"Invalid image data:: {str(e)}")
        return False
    return True


def api_validate_dict_schema(ddict: Dict[str, Any], dataclass_ref: Type):
    """Check if dictionary matches structure of given dataclass.
    Args:
       ddict: dictionary to validate.
       dataclass_ref: dataclass to use as a reference.

    Return: True if dictionary matches dataclass structure, False otherwise.

     How do you valiidated in general dictionnary ?
       --> using dataclass ?

    Example:
        @dataclass
        class User:
            name: str
            age: int

        user_dict = {"name": "John Doe", "age": 30}
        print(valid_json(user_dict, User))

    """
    for f in fields(dataclass_ref):
        if f.name not in ddict:
            loge(f"Invalid json schema, field missing {f.name}")
            return False

        if not isinstance(ddict[f.name], f.type):
            loge(f"Invalid json schema, field type {f.type}")
            return False

    return True
