import pytest

from commons.request_util import RequestUtil


pytestmark = pytest.mark.unit


class FakeResponse:
    """代替 requests 返回的真实响应。"""

    text = "test-response"


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