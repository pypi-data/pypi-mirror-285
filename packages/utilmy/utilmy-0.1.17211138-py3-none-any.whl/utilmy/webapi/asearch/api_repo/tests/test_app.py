import time

from src.api.datamodels import apiEntryURI_v1
from src.utils.util_image import text_to_base64_image
from src.utils.util_log import log


def extract_text_sync(client, image_str):
    """Test synchronous text extraction endpoint."""

    response = client.post(apiEntryURI_v1.imgsync, json={"data": image_str, "token": "test_token"})
    print(response.json())
    assert response.status_code == 200
    return response.json().get("text", "").strip()


def extract_text_async(client, image_str):
    """Test asynchronous text extraction endpoint and retrieve results."""
    response = client.post(apiEntryURI_v1.imgasync, json={"data": image_str, "token": "test_token"})
    assert response.status_code == 200
    job_id = response.json().get("jobid")
    nTry = 10
    while True:
        time.sleep(2)
        nTry -= 1
        if nTry < 0:
            assert False

        # Assuming there's an endpoint to get result of a job by its ID
        result_response = client.post(
            apiEntryURI_v1.imgasyncget, json={"jobid": job_id, "token": "test_token"}
        )
        log(result_response.json())
        assert response.status_code == 200
        res = result_response.json()

        status = res.get("status")
        if status == "in-processing":
            continue

        assert status == "success"
        assert result_response.json()["jobid"] == job_id
        return res.get("text", "").strip()


def test_missing_text_api_result(client):
    res = client.post(apiEntryURI_v1.imgsync, json={"data": "test", "token": "test_token"})
    assert res.status_code != 200


def test_api(client):

    text_sync_test = "test sync"
    image_sync_str = text_to_base64_image(text_sync_test)
    text_1 = extract_text_sync(client, image_sync_str)
    assert text_1 == text_sync_test

    text_async_test = "test async"
    image_async_str = text_to_base64_image(text_async_test)
    text_2 = extract_text_async(client, image_async_str)
    assert text_2 == text_async_test
