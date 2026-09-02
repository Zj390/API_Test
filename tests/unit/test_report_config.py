import platform
import re
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from pytest_metadata.plugin import metadata_key

import conftest as report_config


pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    (
        "marker_expression",
        "expected_scope",
        "expected_title"
    ),
    [
        (
            "unit",
            "框架单元测试",
            "API Test - 框架单元测试报告"
        ),
        (
            "smoke or user",
            "接口自动化测试",
            "API Test - 接口自动化测试报告"
        ),
        (
            "",
            "全部测试",
            "API Test - 全部测试报告"
        )
    ]
)
def test_get_report_labels(
    marker_expression,
    expected_scope,
    expected_title
):
    assert report_config.get_test_scope(
        marker_expression
    ) == expected_scope

    assert report_config.get_report_title(
        marker_expression
    ) == expected_title


def test_configure_report_metadata():
    config = SimpleNamespace(
        option=SimpleNamespace(
            markexpr="unit"
        ),
        stash={
            metadata_key: {
                "旧字段": "应当被清除"
            }
        }
    )

    report_config.pytest_configure(config)

    assert config.stash[metadata_key] == {
        "项目": "API Test",
        "测试范围": "框架单元测试",
        "Python版本": platform.python_version(),
        "pytest版本": pytest.__version__,
        "运行环境": Path(sys.prefix).name,
        "操作系统": platform.system()
    }


def test_set_html_report_title():
    report = SimpleNamespace(
        config=SimpleNamespace(
            option=SimpleNamespace(
                markexpr="smoke or user"
            )
        ),
        title=""
    )

    report_config.pytest_html_report_title(
        report
    )

    assert report.title == (
        "API Test - 接口自动化测试报告"
    )


def test_sensitive_metadata_patterns(
    pytestconfig
):
    patterns = pytestconfig.getini(
        "environment_table_redact_list"
    )

    sensitive_fields = [
        "PASSWORD",
        "user_passwd",
        "api_secret",
        "access_token",
        "Authorization",
        "session_cookie"
    ]

    for field in sensitive_fields:
        assert any(
            re.search(pattern, field)
            for pattern in patterns
        )

    assert not any(
        re.search(pattern, "Python版本")
        for pattern in patterns
    )