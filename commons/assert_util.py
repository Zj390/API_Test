class AssertUtil:

    TYPE_MAP = {        # 本质上是一个转译表
        "list": list,
        "dict": dict,
        "str": str,
        "int": int,
        "float": float,
        "bool": bool
    }

    @staticmethod
    def validate_response(response, validate):
        if not validate:
            return

        supported_rules = {     # 防误写检查
            "status_code",
            "text_contains",
            "exists",
            "not_empty",
            "greater_than",
            "equals",
            "types",
            "list_item_equals"
        }

        assert isinstance(validate, dict), (
            f"validate必须是字典，实际为：{type(validate).__name__}"
        )

        unknown_rules = set(validate) - supported_rules

        assert not unknown_rules, (
            f"存在不支持的断言规则：{unknown_rules}"
        )

        expected_status = validate.get("status_code")
        if expected_status is not None:
            assert response.status_code == expected_status, (
                f"HTTP状态码错误，预期：{expected_status},"
                f"实际：{response.status_code}"
            )

        for expected_text in validate.get("text_contains") or []:
            assert expected_text in response.text, (
                f"响应文本中缺少：{expected_text}"
            )

        json_rules = (
            "exists",
            "not_empty",
            "greater_than",
            "equals",
            "types",
            "list_item_equals"
        )

        if not any(rule in validate for rule in json_rules):
            return

        body = response.json()
        assert isinstance(body, dict), (
            f"json响应不是字典：{body}"
        )       # 不是所有json都是字典，这里只是适用于这几个测试

        for field in validate.get("exists") or []:
            assert field in body, f"响应中缺少字段：{field}, 实际响应：{body}"

        for field in validate.get("not_empty") or []:
            assert field in body, f"响应中缺少字段：{field}"
            assert body[field] not in (None, "", [], {}), (
                f"字段不能为空：{field},实际响应：{body}"
            )

        for field, expected in (validate.get("greater_than") or {}).items():
            assert field in body, f"响应中缺少字段：{field}"
            actual = body[field]
            assert isinstance(actual, (int, float)), (
                f"{field}不是数值：{actual}"
            )
            assert actual > expected, (
                f"{field}应大于{expected},实际为：{actual}"
            )

        for field, expected in (validate.get("equals") or {}).items():
            assert field in body, f"响应中缺少字段：{field}"
            actual = body[field]
            assert actual == expected, (
                f"{field}不符合预期，预期：{expected},实际：{actual}"
            )

        for field, expected_type_name in (validate.get("types") or {}).items():
            assert field in body, f"响应中缺少字段：{field}"
            expected_type = AssertUtil.TYPE_MAP.get(expected_type_name)
            # 这里get(expected_type_name)括号里不用""的原因是expected_type_name本身就是字符串了

            assert expected_type is not None, (
                f"不支持的类型名称：{expected_type_name}"
            )
            assert isinstance(body[field], expected_type), (
                f"{field}类型错误，预期：{expected_type_name},"
                f"实际：{type(body[field]).__name__}"
            )

        if "list_item_equals" in validate:
            AssertUtil._validate_list_item_equals(
                body,
                validate["list_item_equals"]
            )

    @staticmethod
    def _validate_list_item_equals(body, rule):
        """在JSON列表中找到目标字典并检查字段值。"""
        assert isinstance(rule, dict) and rule, (
            "list_item_equals必须是非空字典"
        )

        field = rule.get("field")
        match = rule.get("match")
        expected_values = rule.get("equals")

        assert field, (
            "list_item_equals缺少field配置"
        )

        assert isinstance(match, dict) and match, (
            "list_item_equals的match必须是非空字典"
        )

        assert (
            isinstance(expected_values, dict)
            and expected_values
        ), (
            "list_item_equals的equals必须是非空字典"
        )

        assert field in body, (
            f"响应中缺少列表字段：{field}"
        )

        items = body[field]

        assert isinstance(items, list), (
            f"{field}不是列表：{items}"
        )

        matched_item = next(
            (
                item
                for item in items
                if isinstance(item, dict)
                and all(
                    item.get(key) == expected
                    for key, expected in match.items()
                )
            ),
            None
        )

        assert matched_item is not None, (
            f"{field}中没有找到符合条件的数据：{match}"
        )

        for expected_field, expected in (
            expected_values.items()
        ):
            assert expected_field in matched_item, (
                f"匹配结果中缺少字段：{expected_field}"
            )

            actual = matched_item[expected_field]

            assert actual == expected, (
                f"{expected_field}不符合预期，"
                f"预期：{expected}，实际：{actual}"
            )