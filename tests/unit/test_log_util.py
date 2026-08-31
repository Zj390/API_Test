import pytest

from commons.log_util import LogUtil


pytestmark = pytest.mark.unit


def test_mask_nested_sensitive_data():
    original_data = {
        "params": {
            "appid": "test-appid",
            "access_token": "real-token"
        },
        "data": {
            "username": "test-user",
            "password": "real-password"
        },
        "headers": {
            "Authorization": "Bearer real-token",
            "Cookie": "session=real-cookie"
        },
        "items": [
            {
                "secret": "real-secret",
                "name": "visible-name"
            }
        ]
    }

    result = LogUtil.mask_sensitive_data(original_data)

    assert result == {
        "params": {
            "appid": "test-appid",
            "access_token": "***"
        },
        "data": {
            "username": "test-user",
            "password": "***"
        },
        "headers": {
            "Authorization": "***",
            "Cookie": "***"
        },
        "items": [
            {
                "secret": "***",
                "name": "visible-name"
            }
        ]
    }

    # 脱敏不能修改原始请求，否则会把 "***" 真正发送给接口。
    assert original_data["data"]["password"] == (
        "real-password"
    )


def test_keep_normal_data():
    original_data = {
        "method": "get",
        "url": "https://example.com",
        "timeout": 10
    }

    result = LogUtil.mask_sensitive_data(original_data)

    assert result == original_data
    assert result is not original_data