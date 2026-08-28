import pytest

from commons.config_util import ConfigUtil


pytestmark = pytest.mark.unit


def test_read_environment_variable(monkeypatch):
    # 临时创建环境变量，不依赖真实.env文件。
    monkeypatch.setenv(
        "TEST_USERNAME",
        "test-user"
    )

    result = ConfigUtil.read_env("TEST_USERNAME")

    assert result == "test-user"


def test_environment_variable_not_found(monkeypatch):
    # 确保该变量在本次测试中不存在。
    monkeypatch.delenv(
        "MISSING_VARIABLE",
        raising=False
    )

    with pytest.raises(
        AssertionError,
        match="环境变量不存在或为空"
    ):
        ConfigUtil.read_env("MISSING_VARIABLE")