import pytest

from commons.assert_util import AssertUtil


# 当前文件中的所有测试都属于单元测试。
pytestmark = pytest.mark.unit


class FakeResponse:
    """模拟 requests 返回的 Response 对象。"""

    def __init__(self, status_code=200, body=None, text=""):
        self.status_code = status_code
        self._body = body
        self.text = text

    def json(self):
        # 模拟真实 response.json()。
        # 如果没有提供 JSON 数据，就主动报错，帮助判断代码是否误解析 HTML。
        if self._body is None:
            raise AssertionError("当前响应不应该解析JSON")

        return self._body


def test_validate_all_json_rules():
    # 构造一个同时满足多种断言规则的 JSON 响应。
    response = FakeResponse(
        status_code=200,
        body={
            "access_token": "token-123",
            "expires_in": 7200,
            "errcode": 0,
            "tags": []
        }
    )

    validate = {
        "status_code": 200,
        "exists": [
            "access_token"
        ],
        "not_empty": [
            "access_token"
        ],
        "greater_than": {
            "expires_in": 0
        },
        "equals": {
            "errcode": 0
        },
        "types": {
            "tags": "list"
        }
    }

    # 如果所有规则都满足，validate_response 不会抛出异常，
    # 测试就会通过。
    AssertUtil.validate_response(response, validate)


def test_validate_text_response():
    # 模拟一个返回 HTML 的接口。
    response = FakeResponse(
        status_code=200,
        text='<input name="csrf_token" value="abc123">'
    )

    validate = {
        "status_code": 200,
        "text_contains": [
            "csrf_token"
        ]
    }

    # 这里只配置文本规则，因此 AssertUtil 不应该调用 response.json()。
    AssertUtil.validate_response(response, validate)


def test_status_code_failure():
    response = FakeResponse(
        status_code=500,
        body={}
    )

    validate = {
        "status_code": 200
    }

    # 服务器实际返回500，而预期是200，因此必须触发断言错误。
    # 这里测试的是“错误响应能否被 AssertUtil 发现”。
    with pytest.raises(
        AssertionError,
        match="HTTP状态码错误"
    ):
        AssertUtil.validate_response(response, validate)


def test_equals_failure():
    response = FakeResponse(
        status_code=200,
        body={
            "state": "fail"
        }
    )

    validate = {
        "equals": {
            "state": "success"
        }
    }

    # 实际业务状态是fail，预期是success，应该断言失败。
    with pytest.raises(
        AssertionError,
        match="state不符合预期"
    ):
        AssertUtil.validate_response(response, validate)


def test_unknown_rule_failure():
    response = FakeResponse(
        status_code=200,
        body={}
    )

    validate = {
        # 模拟在 YAML 中把 equals 错写为 equal。
        "equal": {
            "state": "success"
        }
    }

    # AssertUtil 应发现不支持的规则，而不是忽略错误配置。
    with pytest.raises(
        AssertionError,
        match="存在不支持的断言规则"
    ):
        AssertUtil.validate_response(response, validate)


def test_empty_validate():
    response = FakeResponse(
        status_code=500
    )

    # validate为None表示该用例没有配置断言。
    # 此时工具应该直接返回，不解析JSON，也不检查状态码。
    AssertUtil.validate_response(response, None)


def build_tag_response():
    return FakeResponse(
        status_code=200,
        body={
            "tags": [
                {
                    "id": 100,
                    "name": "标签A"
                },
                {
                    "id": 8176,
                    "name": "api_test_8176_updated"
                }
            ]
        }
    )


def build_list_item_rule(expected_name):
    return {
        "list_item_equals": {
            "field": "tags",
            "match": {
                "id": 8176
            },
            "equals": {
                "name": expected_name
            }
        }
    }


def test_list_item_equals_success():
    response = build_tag_response()
    validate = build_list_item_rule(
        "api_test_8176_updated"
    )

    # 找到id=8176，并且名称一致，不应抛出异常。
    AssertUtil.validate_response(
        response,
        validate
    )


def test_list_item_not_found():
    response = build_tag_response()

    validate = {
        "list_item_equals": {
            "field": "tags",
            "match": {
                "id": 9999
            },
            "equals": {
                "name": "不存在的标签"
            }
        }
    }

    with pytest.raises(
        AssertionError,
        match="没有找到符合条件的数据"
    ):
        AssertUtil.validate_response(
            response,
            validate
        )


def test_list_item_value_not_equals():
    response = build_tag_response()
    validate = build_list_item_rule(
        "错误的标签名称"
    )

    with pytest.raises(
        AssertionError,
        match="name不符合预期"
    ):
        AssertUtil.validate_response(
            response,
            validate
        )