import pytest

from commons.extract_util import ExtractUtil


# 当前文件中的所有测试都标记为 unit。
pytestmark = pytest.mark.unit


class FakeResponse:
    """模拟 requests 返回的响应对象。"""

    def __init__(self, body=None, text=""):
        self._body = body
        self.text = text

    def json(self):
        # 模拟 response.json()。
        if self._body is None:
            raise AssertionError("当前响应不应该解析JSON")

        return self._body


@pytest.fixture
def written_data(monkeypatch):
    """
    模拟 write_yaml，并记录 ExtractUtil 准备写入的数据。

    单元测试只检查 ExtractUtil 是否提取出正确内容，
    不应该真的修改 extract.yaml。
    """
    saved_values = []

    # ExtractUtil 在自己的模块中导入了 write_yaml，
    # 所以需要替换 commons.extract_util.write_yaml。
    monkeypatch.setattr(
        "commons.extract_util.write_yaml",
        saved_values.append
    )

    return saved_values


def test_extract_json_value(written_data):
    # 模拟获取token接口的JSON响应。
    response = FakeResponse(
        body={
            "access_token": "token-123",
            "expires_in": 7200
        }
    )

    extract = {
        "access_token": {
            "source": "json",
            "field": "access_token"
        }
    }

    ExtractUtil.extract_and_save(response, extract)

    # write_yaml 应收到提取后的键值对。
    assert written_data == [
        {
            "access_token": "token-123"
        }
    ]


def test_extract_text_value(written_data):
    # 模拟包含csrf_token的HTML响应。
    response = FakeResponse(
        text='<input name="csrf_token" value="csrf-123">'
    )

    extract = {
        "csrf_token": {
            "source": "text",
            "regex": r'name="csrf_token" value="(.*?)"',
            "group": 1
        }
    }

    ExtractUtil.extract_and_save(response, extract)

    assert written_data == [
        {
            "csrf_token": "csrf-123"
        }
    ]


def test_json_field_not_found(written_data):
    response = FakeResponse(
        body={
            "expires_in": 7200
        }
    )

    extract = {
        "access_token": {
            "source": "json",
            "field": "access_token"
        }
    }

    # 响应中没有access_token，应该明确失败。
    with pytest.raises(
        AssertionError,
        match="响应中不存在待提取字段"
    ):
        ExtractUtil.extract_and_save(response, extract)

    # 提取失败后不能写入任何数据。
    assert written_data == []


def test_extracted_value_is_empty(written_data):
    response = FakeResponse(
        body={
            "access_token": ""
        }
    )

    extract = {
        "access_token": {
            "source": "json",
            "field": "access_token"
        }
    }

    with pytest.raises(
        AssertionError,
        match="提取结果不能为空"
    ):
        ExtractUtil.extract_and_save(response, extract)

    assert written_data == []


def test_regex_does_not_match(written_data):
    response = FakeResponse(
        text="<html>没有csrf_token输入框</html>"
    )

    extract = {
        "csrf_token": {
            "source": "text",
            "regex": r'name="csrf_token" value="(.*?)"',
            "group": 1
        }
    }

    with pytest.raises(
        AssertionError,
        match="正则表达式没有匹配到内容"
    ):
        ExtractUtil.extract_and_save(response, extract)

    assert written_data == []


def test_regex_group_not_found(written_data):
    response = FakeResponse(
        text='<input value="csrf-123">'
    )

    extract = {
        "csrf_token": {
            "source": "text",
            "regex": r'value="(.*?)"',
            # 正则只有第1组，却要求读取第2组。
            "group": 2
        }
    }

    with pytest.raises(
        AssertionError,
        match="不存在正则分组"
    ):
        ExtractUtil.extract_and_save(response, extract)

    assert written_data == []


def test_invalid_regex(written_data):
    response = FakeResponse(
        text="<html></html>"
    )

    extract = {
        "csrf_token": {
            "source": "text",
            # 左括号没有闭合，是不合法的正则表达式。
            "regex": "(",
            "group": 1
        }
    }

    with pytest.raises(
        AssertionError,
        match="正则表达式不合法"
    ):
        ExtractUtil.extract_and_save(response, extract)

    assert written_data == []


def test_unsupported_source(written_data):
    response = FakeResponse(
        body={}
    )

    extract = {
        "access_token": {
            # 当前工具只支持json和text。
            "source": "xml",
            "field": "access_token"
        }
    }

    with pytest.raises(
        AssertionError,
        match="不支持的提取来源"
    ):
        ExtractUtil.extract_and_save(response, extract)

    assert written_data == []