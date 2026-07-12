import re
import jsonpath as jsonpath
import requests
import pytest

from commons.request_util import RequestUtil
from commons.yaml_util import write_yaml, read_yaml, clear_yaml, read_yaml_testcase
from commons.assert_util import AssertUtil

class TestApi:


    # 获取access_token鉴权码接口
    @pytest.mark.smoke
    @pytest.mark.parametrize("caseinfo",read_yaml_testcase("testcases/test_get_token.yaml"))
    def test_get_token(self, caseinfo):     # autouse=False时，如此插入夹具
        methods = caseinfo["request"]["method"]
        urls = caseinfo["request"]["url"]
        datas = caseinfo["request"]["params"]

        res = RequestUtil().send_all_request(method=methods, url=urls, params=datas)  # 使用统一封装

        AssertUtil.validate_response(res, caseinfo.get("validate"))

        body = res.json()
        write_yaml({"access_token": body["access_token"]})

    # 查询标签接口
    @pytest.mark.user
    @pytest.mark.parametrize("caseinfo", read_yaml_testcase("testcases/test_select_flag.yaml"))
    def test_select_flag(self,caseinfo):
        methods = caseinfo["request"]["method"]
        urls = caseinfo["request"]["url"]
        datas = caseinfo["request"]["params"]
        datas["access_token"] = read_yaml("access_token")

        res = RequestUtil().send_all_request(method=methods, url=urls, params=datas)
        assert res.status_code == 200, f"HTTP状态码错误：{res.status_code}"

        body = res.json()
        print(body)
        assert "tags" in body, f"响应中没有用tags字段：{body}"
        assert isinstance(body["tags"], list), f"tags不是列表：{body}"


    # 编辑标签接口
    @pytest.mark.user
    @pytest.mark.parametrize("caseinfo", read_yaml_testcase("testcases/test_edit_flag.yaml"))
    def test_edit_flag(self,caseinfo):
        methods = caseinfo["request"]["method"]
        urls = caseinfo["request"]["url"]
        datas1 = caseinfo["request"]["params"]
        datas1["access_token"] = read_yaml("access_token")
        datas2 = caseinfo["request"]["json"]

        res = RequestUtil().send_all_request(method=methods, url=urls, json=datas2, params=datas1)

        assert res.status_code == 200, f"HTTP状态码错误：{res.status_code}"

        body = res.json()

        assert body.get("errcode") == 0, f"编辑标签失败：{body}"
        # 这里是body.get("errcode")而不是body["errcode"]是因为
        # 前者在errcode不存在时不会报错，只会返回None，而后者会报错，相当于同时判断是否存在
        assert body.get("errmsg") == "ok", f"错误信息异常：{body}"

    # 访问phpwind首页接口
    @pytest.mark.smoke
    @pytest.mark.parametrize("caseinfo", read_yaml_testcase("testcases/test_phpwind.yaml"))
    def test_phpwind(self,caseinfo):
        methods = caseinfo["request"]["method"]
        urls = caseinfo["request"]["url"]

        res = RequestUtil().send_all_request(method=methods, url=urls)

        assert res.status_code == 200, f"访问网页失败：{res.status_code}"

        result = re.search(
            'name="csrf_token" value="(.*?)"', res.text
        )

        assert result is not None, f"页面中没有找到csrf_token"
        assert result.group(1), f"csrf_token不能为空"

        write_yaml({"csrf_token": result.group(1)})

    # 登陆接口
    @pytest.mark.user
    @pytest.mark.parametrize("caseinfo", read_yaml_testcase("testcases/test_login.yaml"))
    def test_login(self,caseinfo):
        methods = caseinfo["request"]["method"]
        urls = caseinfo["request"]["url"]
        headers = caseinfo["request"]["headers"]
        datas = caseinfo["request"]["params"]
        datas["csrf_token"] = read_yaml("csrf_token")

        res = RequestUtil().send_all_request(method=methods, url=urls, headers=headers, data=datas)

        assert res.status_code == 200, f"HTTP状态码错误：{res.status_code}"

        body = res.json()

        assert body.get("state") == "success", f"登陆失败：{body}"