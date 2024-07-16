from fastapi import HTTPException

from src.api.authenticate import api_authenticate


def test_api_authenticate() -> None:
    try:
        res = api_authenticate({}, "", "name")
    except HTTPException as e:
        assert e.status_code == 401
        assert e.detail == "Token is required."
