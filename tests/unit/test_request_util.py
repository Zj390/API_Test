import pytest
import logging
import requests

from commons.request_util import RequestUtil


pytestmark = pytest.mark.unit


class FakeResponse:
    """代替 requests 返回的真实响应。"""

    text = "test-response"
    status_code = 200


@pytest.fixture
def captured_request(monkeypatch):
    """
    拦截 Session.request，不发送真实网络请求，
    并保存 RequestUtil 最终传入的参数。
    """
    captured_kwargs = {}

    def fake_request(**kwargs):
        captured_kwargs.update(kwargs)
        return FakeResponse()

    monkeypatch.setattr(
        RequestUtil.sess,
        "request",
        fake_request
    )

    return captured_kwargs


def test_use_default_timeout(captured_request):
    RequestUtil().send_all_request(
        method="get",
        url="https://example.com"
    )

    assert captured_request["timeout"] == 10


def test_keep_custom_timeout(captured_request):
    RequestUtil().send_all_request(
        method="get",
        url="https://example.com",
        timeout=20
    )

    assert captured_request["timeout"] == 20


def test_request_log_masks_sensitive_data(
    captured_request,
    caplog
):
    caplog.set_level(
        logging.INFO,
        logger="commons.request_util"
    )

    RequestUtil().send_all_request(
        method="post",
        url=(
            "https://example.com/login"
            "?access_token=url-token"
        ),
        params={
            "access_token": "real-token"
        },
        data={
            "username": "test-user",
            "password": "real-password"
        },
        headers={
            "Authorization": "Bearer real-token"
        }
    )

    log_text = caplog.text

    # 敏感值不能出现在日志中。
    assert "url-token" not in log_text
    assert "real-token" not in log_text
    assert "real-password" not in log_text

    # 日志中应该出现脱敏符号和响应状态码。
    assert "***" in log_text
    assert "status_code=200" in log_text

    # response.text 不再被日志记录。
    assert "test-response" not in log_text

    # 真正发送的数据不能被替换成 "***"。
    assert (
        captured_request["data"]["password"]
        == "real-password"
    )


def test_request_exception_log(monkeypatch, caplog):
    def fake_request(**kwargs):
        raise requests.Timeout(
            "sensitive-error-message"
        )

    monkeypatch.setattr(
        RequestUtil.sess,
        "request",
        fake_request
    )

    caplog.set_level(
        logging.INFO,
        logger="commons.request_util"
    )

    with pytest.raises(requests.Timeout):
        RequestUtil().send_all_request(
            method="get",
            url="https://example.com"
        )

    assert "请求失败：Timeout" in caplog.text
    assert "sensitive-error-message" not in caplog.text