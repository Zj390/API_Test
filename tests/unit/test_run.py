from datetime import datetime

import pytest

import run


pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    ("args", "expected"),
    [
        (["-m", "unit"], "unit"),
        (["-m=smoke"], "smoke"),
        ([], "")
    ]
)
def test_get_marker_expression(
    args,
    expected
):
    result = run.get_marker_expression(args)

    assert result == expected


@pytest.mark.parametrize(
    ("command_args", "report_type"),
    [
        (["-m", "unit"], "unit"),
        (["-m", "smoke or user"], "api"),
        ([], "all")
    ]
)
def test_build_automatic_report_args(
    command_args,
    report_type,
    monkeypatch,
    tmp_path
):
    monkeypatch.setattr(
        run,
        "get_project_path",
        lambda relative_path: tmp_path / relative_path
    )

    current_time = datetime(
        2026,
        9,
        1,
        20,
        30,
        45
    )

    args = run.build_pytest_args(
        command_args,
        current_time
    )

    expected_report = (
        tmp_path
        / "reports"
        / (
            f"{report_type}_report_"
            "20260901_203045.html"
        )
    )

    assert command_args == args[:len(command_args)]
    assert f"--html={expected_report}" in args
    assert "--self-contained-html" in args
    assert expected_report.parent.exists()


def test_keep_manual_html_report_path(
    monkeypatch,
    tmp_path
):
    monkeypatch.setattr(
        run,
        "get_project_path",
        lambda relative_path: tmp_path / relative_path
    )

    command_args = [
        "-m",
        "unit",
        "--html=custom-report.html"
    ]

    args = run.build_pytest_args(command_args)

    assert args == command_args
    assert not (tmp_path / "reports").exists()