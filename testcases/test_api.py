import pytest

from commons.request_util import RequestUtil
from commons.yaml_util import read_yaml_testcase
from commons.assert_util import AssertUtil
from commons.extract_util import ExtractUtil
from commons.replace_util import ReplaceUtil


class TestApi:

    # 获取access_token鉴权码接口
    @pytest.mark.smoke
    @pytest.mark.parametrize("caseinfo", read_yaml_testcase("testcases/test_get_token.yaml"))
    def test_get_token(self, caseinfo):     # autouse=False时，如此插入夹具
        request_data = ReplaceUtil.replace_variables(caseinfo["request"])

        res = RequestUtil().send_all_request(**request_data)  # 使用统一封装

        AssertUtil.validate_response(res, caseinfo.get("validate"))

        ExtractUtil.extract_and_save(res, caseinfo.get("extract"))

    # 查询标签接口
    @pytest.mark.user
    @pytest.mark.parametrize("caseinfo", read_yaml_testcase("testcases/test_select_flag.yaml"))
    def test_select_flag(self, caseinfo):
        request_data = ReplaceUtil.replace_variables(caseinfo["request"])

        res = RequestUtil().send_all_request(**request_data)

        AssertUtil.validate_response(res, caseinfo.get("validate"))

    # 编辑标签接口
    @pytest.mark.user
    @pytest.mark.parametrize("caseinfo", read_yaml_testcase("testcases/test_edit_flag.yaml"))
    def test_edit_flag(self, caseinfo):
        request_data = ReplaceUtil.replace_variables(caseinfo["request"])

        res = RequestUtil().send_all_request(**request_data)

        AssertUtil.validate_response(res, caseinfo.get("validate"))

    # 访问phpwind首页接口
    @pytest.mark.smoke
    @pytest.mark.parametrize("caseinfo", read_yaml_testcase("testcases/test_phpwind.yaml"))
    def test_phpwind(self, caseinfo):
        request_data = ReplaceUtil.replace_variables(caseinfo["request"])

        res = RequestUtil().send_all_request(**request_data)

        AssertUtil.validate_response(res, caseinfo.get("validate"))

        ExtractUtil.extract_and_save(res, caseinfo.get("extract"))

    # 登陆接口
    @pytest.mark.user
    @pytest.mark.parametrize("caseinfo", read_yaml_testcase("testcases/test_login.yaml"))
    def test_login(self, caseinfo):
        request_data = ReplaceUtil.replace_variables(caseinfo["request"])

        res = RequestUtil().send_all_request(**request_data)

        AssertUtil.validate_response(res, caseinfo.get("validate"))
