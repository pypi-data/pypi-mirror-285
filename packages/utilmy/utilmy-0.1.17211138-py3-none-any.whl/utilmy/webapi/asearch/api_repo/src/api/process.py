# -*- coding: utf-8 -*-
import base64
import io
import time

import fire
from fastapi import BackgroundTasks
from PIL import Image
from PIL.Image import Image as ImageType

from src.api.datamodels import imgasyncGetOutput, imgasyncOutput, imgsyncOutput
from src.engine.ocr.tessaract.process import extract_text_from_image
from src.utils.util_base import uniqueid_create
from src.utils.util_log import log, loge, logw
from src.utils.util_storage import Storage


###################################################################################
def api_imgsync_process(
    cfg: dict,
    image_str: str,
    lang=None,
) -> imgsyncOutput:
    """Process image data and return extracted text.
    Args:
        image_data (ImageData): image data to be processed.
        lang (str, optional): language of image data. Defaults to None.

    Returns:
        - imgsyncOutput: an dict dataclass containing results.

    Raises:
        valueError: If image data is invalid.
    """
    try:
        extracted_text = image_extract_text(image_str)

        json_val = imgsyncOutput(text=extracted_text, ts=float(time.time()))

        return json_val

    except Exception as e:
        raise ValueError(f"Error image processing: {e}")


def api_imgasync_process(
    cfg: dict, image_str: str, background_tasks: BackgroundTasks, lang=None, storage=None
) -> imgasyncOutput:
    """API function that processes an image asynchronously.

    Args:
        - cfg: dictionary containing configuration settings
        - image_str: a base64 encoded image string
        - background_tasks: BackgroundTasks object for handling tasks in background
        - lang: optional parameter indicating language
        - storage: optional parameter for storage configuration

    Returns:
        - imgsyncOutput: an dict dataclass containing results.

    Raises:
        valueError: If image data is invalid.

    TODO: check number of tasks < max_tasks
          max_tasks = cfg["service"]["max_tasks"]
    """
    try:

        jobid = uniqueid_create()

        ##TODO: Add counter of Active task < max_task to prevent server overload.
        background_tasks.add_task(image_extract_text_async, image_str, jobid, storage)

        return imgasyncOutput(jobid=jobid, ts=float(time.time()))

    except Exception as e:
        raise ValueError(f"Invalid image data: {e}")


def api_imgasyncget_process(jobid: str, storage: Storage) -> imgasyncGetOutput:
    """Get an imgasync output based on job id using provided storage.
    Args:
        jobid: id of job.
        storage: storage object.

    Returns:
        imgasyncGetOutput: imgasync output.
    """
    try:
        ddict: dict = storage.get(jobid)

        json_val = imgasyncGetOutput(
            jobid=jobid,
            text=ddict["text"],
            status=ddict["status"],
            ts=float(time.time()),
        )
        return json_val

    except Exception as e:
        raise ValueError(f"jobid {jobid} not found, {e}")


###################################################################################
def image_extract_text(image_str: str) -> str:
    """Extracts text from an image encoded as a base64 string.
    Args:
        image_str (str): base64-encoded image string. Assume image is correct.

    Returns:
        str: extracted text from image.


    """
    image_bytes = base64.b64decode(image_str)
    image: ImageType = Image.open(io.BytesIO(image_bytes))
    text = extract_text_from_image(image)

    return text


def image_extract_text_async(image_str: str, jobid: str, storage):
    """extracts text from an image.
    Args:
        image_str (str): base64 encoded string representation of image.
        job_id (str): ID of job.
        storage: storage object used to store job status and extracted text.

    Returns:
        None

    TODO:
        - Set up a time limit for job.
        - Normalize JSON return message.
        - Add logging.
    """

    try:
        log(f"Starting async job: {jobid}")
        storage.put(jobid, {"status": "processing", "text": ""})

        text = image_extract_text(image_str)

        log(f"Ending async job: {jobid}")
        storage.put(jobid, {"status": "success", "text": text})

    except Exception as e:
        logw(e)
        storage.put(jobid, {"status": "failure", "text": str(e)})
        return


####################################################################################
if __name__ == "__main__":
    fire.Fire()
