import platform
import sys
from pathlib import Path

import pytest
from pytest_metadata.plugin import metadata_key


def get_test_scope(marker_expression):
    """根据pytest标记判断本次测试范围。"""
    marker_expression = marker_expression.strip()

    if marker_expression == "unit":
        return "框架单元测试"

    if marker_expression:
        return "接口自动化测试"

    return "全部测试"


def get_report_title(marker_expression):
    """根据测试范围生成HTML报告标题。"""
    test_scope = get_test_scope(marker_expression)

    return f"API Test - {test_scope}报告"


@pytest.hookimpl(trylast=True)
def pytest_configure(config):
    """设置HTML报告中展示的非敏感环境信息。"""
    marker_expression = (
        config.option.markexpr or ""
    )

    metadata = config.stash[metadata_key]
    metadata.clear()

    metadata["项目"] = "API Test"
    metadata["测试范围"] = get_test_scope(
        marker_expression
    )
    metadata["Python版本"] = (
        platform.python_version()
    )
    metadata["pytest版本"] = pytest.__version__
    metadata["运行环境"] = Path(
        sys.prefix
    ).name
    metadata["操作系统"] = platform.system()


def pytest_html_report_title(report):
    """设置HTML页面标题。"""
    marker_expression = (
        report.config.option.markexpr or ""
    )

    report.title = get_report_title(
        marker_expression
    )