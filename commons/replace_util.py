from commons.yaml_util import read_yaml


class ReplaceUtil:  # 用来对于YAML用例上request部分数据进行提取

    @staticmethod
    def replace_variables(data):
        # 如果是字典，继续处理字典中的每个值
        if isinstance(data, dict):
            new_data = {}

            for key, value in data.items():
                new_data[key] = ReplaceUtil.replace_variables(value)

            return new_data

        # 如果是列表，继续处理列表这种的每个元素
        if isinstance(data, list):
            new_list = []

            for value in data:
                new_list.append(
                    ReplaceUtil.replace_variables(value)
                )

            return new_list


        if (
            isinstance(data, str)
            and data.startswith("${")
            and data.endswith("}")
        ):      # 就是在查找带“${}”的字符串，然后定位到它对应的参数名方便后续提取
            variable_name = data[2:-1]

            assert variable_name, f"变量名不能为空"

            return read_yaml(variable_name)

        # 普通字符串、数字、None等数据保持原样
        return data