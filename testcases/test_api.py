import re
import jsonpath as jsonpath
import requests
import pytest

from commons.request_util import RequestUtil
from commons.yaml_util import write_yaml, read_yaml, clear_yaml, read_yaml_testcase
from commons.assert_util import AssertUtil
from commons.extract_util import ExtractUtil


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

        ExtractUtil.extract_and_save(res, caseinfo.get("extract"))

    # 查询标签接口
    @pytest.mark.user
    @pytest.mark.parametrize("caseinfo", read_yaml_testcase("testcases/test_select_flag.yaml"))
    def test_select_flag(self, caseinfo):
        methods = caseinfo["request"]["method"]
        urls = caseinfo["request"]["url"]
        datas = caseinfo["request"]["params"]
        datas["access_token"] = read_yaml("access_token")

        res = RequestUtil().send_all_request(method=methods, url=urls, params=datas)

        AssertUtil.validate_response(res, caseinfo.get("validate"))


    # 编辑标签接口
    @pytest.mark.user
    @pytest.mark.parametrize("caseinfo", read_yaml_testcase("testcases/test_edit_flag.yaml"))
    def test_edit_flag(self, caseinfo):
        methods = caseinfo["request"]["method"]
        urls = caseinfo["request"]["url"]
        datas1 = caseinfo["request"]["params"]
        datas1["access_token"] = read_yaml("access_token")
        datas2 = caseinfo["request"]["json"]

        res = RequestUtil().send_all_request(method=methods, url=urls, json=datas2, params=datas1)

        AssertUtil.validate_response(res, caseinfo.get("validate"))

    # 访问phpwind首页接口
    @pytest.mark.smoke
    @pytest.mark.parametrize("caseinfo", read_yaml_testcase("testcases/test_phpwind.yaml"))
    def test_phpwind(self,caseinfo):
        methods = caseinfo["request"]["method"]
        urls = caseinfo["request"]["url"]

        res = RequestUtil().send_all_request(method=methods, url=urls)

        AssertUtil.validate_response(res, caseinfo.get("validate"))

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

        AssertUtil.validate_response(res, caseinfo.get("validate"))
