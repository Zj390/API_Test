import re

from commons.yaml_util import write_yaml


class ExtractUtil:  # 用来识别用例上需要提取并保存的数据，然后把它保存下来

    @staticmethod
    def _extract_json_value(
            body,
            variable_name,
            rule
    ):
        """从JSON字段或字段中的列表元素提取数据。"""
        assert isinstance(body, dict), (
            f"json响应不是字典：{body}"
        )

        field = rule.get("field")

        assert field, (
            f"{variable_name}缺少field配置"
        )

        assert field in body, (
            f"响应中不存在待提取字段：{field},"
            f"实际响应：{body}"
        )

        value = body[field]
        match = rule.get("match")

        # 没有match时，保持原来的直接字段提取方式。
        if match is None:
            return value

        assert isinstance(match, dict) and match, (
            f"{variable_name}的match必须是非空字典"
        )

        assert isinstance(value, list), (
            f"{field}不是列表，无法按条件查找"
        )

        matched_item = next(    # next():取第一个符合条件的元素
            (
                item
                for item in value       # 先遍历每一个标签字典，这里的value就是响应中的不同标签
                if isinstance(item, dict)   # 确认必须是字典
                and all(
                    item.get(key) == expected   # 这步是找到那个对应的那个标签名如：“id：8176”
                    for key, expected in match.items()
                )
            ),
            None
        )       # 最终输出的则是那个被选中的完全匹配的标签，并把它保存下来
        # 如这里matched_item = {"id": 8176,"name": "原始标签"}

        assert matched_item is not None, (
            f"{field}中没有找到符合条件的数据：{match}"
        )

        value_field = rule.get("value_field")

        assert value_field, (
            f"{variable_name}缺少value_field配置"
        )

        assert value_field in matched_item, (
            f"匹配结果中不存在字段：{value_field},"
            f"实际结果：{matched_item}"
        )

        return matched_item[value_field]    # 返回要改标签对应的真正值

    @staticmethod
    def extract_and_save(response, extract):
        if not extract:
            return

        assert isinstance(extract, dict), (
            f"extract必须是字典：{type(extract).__name__}"
        )

        extracted_values = {}

        for variable_name, rule in extract.items():
            assert isinstance(rule, dict), (
                f"{variable_name}的提取规则必须是字典"
            )

            source = rule.get("source")

            assert source in ("json", "text"), (
                f"不支持的提取来源：{source}"
            )

            if source == "json":
                body = response.json()

                value = ExtractUtil._extract_json_value(
                    body,
                    variable_name,
                    rule
                )

            else:
                pattern = rule.get("regex")
                group = rule.get("group", 1)

                assert pattern, (
                    f"{variable_name}缺少regex配置"
                )

                assert isinstance(group, int) and group >= 0, (
                    f"{variable_name}的group必须是非负整数，"
                    f"实际是：{group}"
                )

                try:
                    result = re.search(pattern, response.text)
                except re.error as error:
                    raise AssertionError(
                        f"{variable_name}正则表达式不合法：{error}"
                    ) from error

                assert result is not None, (
                    f"正则表达式没有匹配到内容：{pattern}"
                )

                try:
                    value = result.group(group)
                except IndexError as error:
                    raise AssertionError(
                        f"{variable_name}不存在正则分组：{group}"
                    ) from error

            assert value not in (None, {}, [], ""), (
                f"提取结果不能为空：{variable_name}"
            )

            extracted_values[variable_name] = value     # 这里保存下每个需要提取的键值对

        write_yaml(extracted_values)