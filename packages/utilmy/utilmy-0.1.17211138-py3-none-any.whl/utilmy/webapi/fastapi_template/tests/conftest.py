import os

import pytest
from fastapi.testclient import TestClient

os.environ["config_fastapi"] = "config/local/config_pytest.yaml"

from src.app import app
from src.utils.util_config import config_load
from src.utils.util_storage import Storage


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="module")
def cfg():
    return cfgdict


@pytest.fixture(scope="module")
def storage():
    return Storage(cfgdict)
