import pytest

from commons.case_runner import CaseRunner


pytestmark = pytest.mark.unit


@pytest.fixture
def lifecycle_case():
    return {
        "variables": {
            "target_tag_id": 8176
        },
        "setup": {
            "request": {
                "url": "setup"
            }
        },
        "request": {
            "url": "main"
        },
        "verify": {
            "request": {
                "url": "verify"
            }
        },
        "cleanup": {
            "request": {
                "url": "cleanup"
            }
        }
    }


def test_execute_case_lifecycle_order(
    lifecycle_case,
    monkeypatch
):
    executed_steps = []

    def fake_execute_step(step, variables):
        step_name = step["request"]["url"]
        executed_steps.append(step_name)
        return step_name

    monkeypatch.setattr(
        CaseRunner,
        "execute_step",
        fake_execute_step
    )

    response = CaseRunner.execute_case(
        lifecycle_case
    )

    assert response == "main"
    assert executed_steps == [
        "setup",
        "main",
        "verify",
        "cleanup"
    ]


def test_cleanup_runs_when_verify_fails(
    lifecycle_case,
    monkeypatch
):
    executed_steps = []

    def fake_execute_step(step, variables):
        step_name = step["request"]["url"]
        executed_steps.append(step_name)

        if step_name == "verify":
            raise AssertionError("模拟回查失败")

        return step_name

    monkeypatch.setattr(
        CaseRunner,
        "execute_step",
        fake_execute_step
    )

    with pytest.raises(
        AssertionError,
        match="模拟回查失败"
    ):
        CaseRunner.execute_case(
            lifecycle_case
        )

    assert executed_steps == [
        "setup",
        "main",
        "verify",
        "cleanup"
    ]


def test_execute_step_full_process(monkeypatch):
    original_step = {
        "request": {
            "method": "post",
            "json": {
                "id": "${target_tag_id}"
            }
        },
        "validate": {
            "status_code": 200
        },
        "extract": {
            "result_id": {
                "source": "json",
                "field": "id"
            }
        }
    }

    replaced_step = {
        "request": {
            "method": "post",
            "json": {
                "id": 8176
            }
        },
        "validate": {
            "status_code": 200
        },
        "extract": original_step["extract"]
    }

    variables = {
        "target_tag_id": 8176
    }

    fake_response = object()
    executed_actions = []

    def fake_replace(data, received_variables):
        executed_actions.append(
            ("replace", data, received_variables)
        )
        return replaced_step

    def fake_request(self, **kwargs):
        executed_actions.append(
            ("request", kwargs)
        )
        return fake_response

    def fake_validate(response, validate):
        executed_actions.append(
            ("validate", response, validate)
        )

    def fake_extract(response, extract):
        executed_actions.append(
            ("extract", response, extract)
        )

    monkeypatch.setattr(
        "commons.case_runner.ReplaceUtil.replace_variables",
        fake_replace
    )
    monkeypatch.setattr(
        "commons.case_runner.RequestUtil.send_all_request",
        fake_request
    )
    monkeypatch.setattr(
        "commons.case_runner.AssertUtil.validate_response",
        fake_validate
    )
    monkeypatch.setattr(
        "commons.case_runner.ExtractUtil.extract_and_save",
        fake_extract
    )

    result = CaseRunner.execute_step(
        original_step,
        variables
    )

    assert result is fake_response

    assert executed_actions == [
        ("replace", original_step, variables),
        ("request", replaced_step["request"]),
        (
            "validate",
            fake_response,
            replaced_step["validate"]
        ),
        (
            "extract",
            fake_response,
            replaced_step["extract"]
        )
    ]