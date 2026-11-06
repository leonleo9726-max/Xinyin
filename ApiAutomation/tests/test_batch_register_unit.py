import base64

import batch_register
import pytest


pytestmark = pytest.mark.unit


def test_registration_payload_omits_password_and_uses_china_area_code():
    payload = batch_register.create_register_params(
        phone_number="13510011002",
        unique_id="device-id",
    )

    assert payload["stayAreaCode"] == "86"
    assert "stayPassword" not in payload
    assert payload["stayLoginPwdType"] == 1


def test_first_password_payload_uses_password_login_mode():
    payload = batch_register.create_first_password_params(
        phone_number="13510011002",
        unique_id="device-id",
    )

    assert payload["areaCode"] == "86"
    assert payload["uniqueId"] == "device-id"
    assert payload["password"] == base64.b64encode(b"a123456").decode("ascii")
    assert payload["loginPwdType"] == 1


def test_execute_registration_completes_first_password_login(monkeypatch):
    requests = []

    def fake_post(**kwargs):
        url = kwargs["url"]
        data = kwargs["data"]
        requests.append((url, data))
        return {"stayCode": 0, "stayIsSuccess": True}

    monkeypatch.setattr(batch_register.HttpUtils, "post", fake_post)

    result = batch_register.execute_registration(
        {"phone_number": "13510011002", "uniqueId": "device-id"},
        encrypt_key="test-key",
        delay=0,
        area_code="86",
        password="a123456",
    )

    assert result["ok"] is True
    assert len(requests) == 4

    assert requests[0][1]["areaCode"] == "86"
    assert requests[0][1]["userSmsType"] == 0

    assert requests[1][1]["stayAreaCode"] == "86"
    assert "stayPassword" not in requests[1][1]
    assert requests[1][1]["stayLoginPwdType"] == 1

    assert requests[2][1]["areaCode"] == "86"
    assert requests[2][1]["userSmsType"] == 3

    assert requests[3][1]["areaCode"] == "86"
    assert requests[3][1]["uniqueId"] == "device-id"
    assert requests[3][1]["password"] == base64.b64encode(b"a123456").decode("ascii")
    assert requests[3][1]["loginPwdType"] == 1


@pytest.mark.parametrize(
    ("responses", "expected_stage"),
    [
        (
            [
                {"stayCode": 0, "stayIsSuccess": True},
                {"stayCode": 0, "stayIsSuccess": True},
                {"stayCode": 500, "stayIsSuccess": False},
            ],
            "send_first_password_code",
        ),
        (
            [
                {"stayCode": 0, "stayIsSuccess": True},
                {"stayCode": 0, "stayIsSuccess": True},
                {"stayCode": 0, "stayIsSuccess": True},
                {"stayCode": 500, "stayIsSuccess": False},
            ],
            "first_password_login",
        ),
    ],
)
def test_execute_registration_reports_first_password_failure_stage(
    monkeypatch,
    responses,
    expected_stage,
):
    pending_responses = iter(responses)

    def fake_post(**_kwargs):
        return next(pending_responses)

    monkeypatch.setattr(batch_register.HttpUtils, "post", fake_post)

    result = batch_register.execute_registration(
        {"phone_number": "13510011002", "uniqueId": "device-id"},
        encrypt_key="test-key",
        delay=0,
        area_code="86",
        password="a123456",
    )

    assert result["ok"] is False
    assert result["stage"] == expected_stage
