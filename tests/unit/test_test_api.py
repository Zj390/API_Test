import pytest

from testcases import test_api


pytestmark = pytest.mark.unit


def test_build_test_params_adds_dependency_marks(
    monkeypatch
):
    cases = [
        {
            "title": "获取token",
            "marks": ["smoke"],
            "case_id": "get_token"
        },
        {
            "title": "查询标签",
            "marks": ["user"],
            "case_id": "select_tags",
            "depends_on": ["get_token"]
        }
    ]

    monkeypatch.setattr(
        test_api,
        "read_all_yaml_testcases",
        lambda paths: cases
    )

    test_params = test_api.build_test_params()

    assert [param.id for param in test_params] == [
        "获取token",
        "查询标签"
    ]

    first_dependency_mark = test_params[0].marks[1]
    second_dependency_mark = test_params[1].marks[1]

    assert first_dependency_mark.kwargs == {
        "name": "get_token",
        "depends": []
    }

    assert second_dependency_mark.kwargs == {
        "name": "select_tags",
        "depends": ["get_token"]
    }