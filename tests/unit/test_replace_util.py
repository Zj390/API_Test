import pytest

from commons.replace_util import ReplaceUtil


# 给当前文件中的所有测试统一添加 unit 标记。
# 以后可以根据该标记只运行框架单元测试。
pytestmark = pytest.mark.unit   # 给测试贴上“unit”标签


def test_replace_nested_variables(monkeypatch):
    # 保证嵌套字典和列表能正确替换
    # 模拟 extract.yaml 中已经保存的数据。
    # 这样测试不依赖真实文件，也不需要真实 access_token。
    variables = {
        "access_token": "token-123",
        "user_id": 1001
    }

    def fake_read_yaml(key):
        # ReplaceUtil 读取变量时，返回模拟字典中的值。
        return variables[key]

    # 临时用 fake_read_yaml 替换 ReplaceUtil 实际使用的 read_yaml。
    # 替换只在本次测试中有效，测试结束后 pytest 会自动恢复。
    monkeypatch.setattr(
        "commons.replace_util.read_yaml",
        fake_read_yaml
    )

    # 构造一份包含嵌套字典和列表的请求数据。
    original_data = {
        "method": "post",
        "params": {
            "access_token": "${access_token}",
            "user_ids": [
                "${user_id}",
                2002
            ]
        }
    }

    # 调用真正需要测试的变量替换方法。
    result = ReplaceUtil.replace_variables(original_data)

    # 验证动态变量已经替换为模拟数据。
    assert result == {
        "method": "post",
        "params": {
            "access_token": "token-123",
            "user_ids": [
                1001,
                2002
            ]
        }
    }

    # 验证原始数据没有被直接修改。
    # 否则同一个 YAML 用例再次执行时，变量表达式可能已经丢失。
    assert original_data["params"]["access_token"] == (
        "${access_token}"
    )


def test_keep_normal_values():
    # 普通字符串、数字和 None 保持不变。
    original_data = {
        "method": "get",
        "timeout": 10,
        "headers": None
    }

    result = ReplaceUtil.replace_variables(original_data)

    # 新数据的内容应该与原始数据相同。
    assert result == original_data

    # 但它们不应是同一个字典对象，
    # 这说明 ReplaceUtil 创建了新字典。
    assert result is not original_data


def test_empty_variable_name():
    # ${} 外形像变量表达式，但其中没有变量名。
    # pytest.raises 表示这里必须抛出 AssertionError。
    with pytest.raises(
        AssertionError,
        match="变量名不能为空"
    ):
        ReplaceUtil.replace_variables("${}")


def test_replace_environment_variable(monkeypatch):
    environment_variables = {
        "WECHAT_APPID": "test-appid"
    }

    def fake_read_env(key):
        return environment_variables[key]

    # ReplaceUtil 使用的是导入到自身模块中的 ConfigUtil。
    monkeypatch.setattr(
        "commons.replace_util.ConfigUtil.read_env",
        fake_read_env
    )

    original_data = {
        "appid": "${env:WECHAT_APPID}"
    }

    result = ReplaceUtil.replace_variables(original_data)

    assert result == {
        "appid": "test-appid"
    }

    # 原始数据仍然不能被修改。
    assert original_data == {
        "appid": "${env:WECHAT_APPID}"
    }


def test_replace_case_variables(monkeypatch):
    case_variables = {
        "target_tag_id": 8176,
        "test_tag_name": "api_test_8176"
    }

    # 当前两个变量都存在于局部variables中，
    # 因此不应该访问extract.yaml。
    def fail_read_yaml(key):
        raise AssertionError(
            f"不应该读取extract.yaml：{key}"
        )

    monkeypatch.setattr(
        "commons.replace_util.read_yaml",
        fail_read_yaml
    )

    original_data = {
        "match": {
            "id": "${target_tag_id}"
        },
        "json": {
            "tag": {
                "id": "${target_tag_id}",
                "name": "${test_tag_name}"
            }
        }
    }

    result = ReplaceUtil.replace_variables(
        original_data,
        case_variables
    )

    assert result == {
        "match": {
            "id": 8176
        },
        "json": {
            "tag": {
                "id": 8176,
                "name": "api_test_8176"
            }
        }
    }

    # ID必须保持整数类型。
    assert isinstance(
        result["json"]["tag"]["id"],
        int
    )

    # 原始YAML数据不能被直接修改。
    assert original_data["json"]["tag"]["id"] == (
        "${target_tag_id}"
    )


def test_case_variables_must_be_dictionary():
    with pytest.raises(
        AssertionError,
        match="variables必须是字典"
    ):
        ReplaceUtil.replace_variables(
            "${target_tag_id}",
            variables=["not", "a", "dictionary"]
        )