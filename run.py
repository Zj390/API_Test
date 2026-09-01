import sys
from datetime import datetime

import pytest

from commons.path_util import get_project_path


def get_marker_expression(args):
    """读取-m后面的pytest标记表达式。"""
    for index, argument in enumerate(args):
        if argument == "-m" and index + 1 < len(args):
            return args[index + 1]

        if argument.startswith("-m="):
            return argument[3:]

    return ""


def build_pytest_args(
    command_args=None,
    current_time=None
):
    """保留原有参数，并自动添加HTML报告参数。"""
    if command_args is None:
        command_args = sys.argv[1:]

    args = list(command_args)

    # 用户已经指定报告路径时，不再重复添加。
    if any(
        argument == "--html"
        or argument.startswith("--html=")
        for argument in args
    ):
        return args

    marker_expression = get_marker_expression(args)

    if marker_expression.strip() == "unit":
        report_type = "unit"
    elif marker_expression:
        report_type = "api"
    else:
        report_type = "all"

    if current_time is None:
        current_time = datetime.now()

    timestamp = current_time.strftime(
        "%Y%m%d_%H%M%S"
    )

    report_dir = get_project_path("reports")
    report_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    report_path = (
        report_dir
        / f"{report_type}_report_{timestamp}.html"
    )

    args.extend([
        f"--html={report_path}",
        "--self-contained-html"
    ])

    return args


if __name__ == "__main__":
    raise SystemExit(
        pytest.main(build_pytest_args())
    )