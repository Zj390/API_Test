from commons.yaml_util import read_yaml
from commons.config_util import ConfigUtil


class ReplaceUtil:  # 用来对于YAML用例上request部分数据进行提取
    """递归替换YAML数据中的变量表达式。"""

    @staticmethod
    def replace_variables(data, variables=None):
        """
        variables保存当前用例的局部变量。

        不在局部变量中的普通变量，会继续从extract.yaml读取。
        """
        if variables is None:
            variables = {}

        assert isinstance(variables, dict), (
            "variables必须是字典"
        )

        if isinstance(data, dict):
            new_data = {}

            for key, value in data.items():
                new_data[key] = (
                    ReplaceUtil.replace_variables(
                        value,
                        variables
                    )
                )

            return new_data

        if isinstance(data, list):
            return [
                ReplaceUtil.replace_variables(
                    value,
                    variables
                )
                for value in data
            ]

        if isinstance(data, tuple):
            return tuple(
                ReplaceUtil.replace_variables(
                    value,
                    variables
                )
                for value in data
            )

        if (
            isinstance(data, str)
            and data.startswith("${")
            and data.endswith("}")
        ):
            variable_name = data[2:-1]

            assert variable_name, "变量名不能为空"

            if variable_name.startswith("env:"):
                environment_name = variable_name[4:]

                assert environment_name, (
                    "环境变量名不能为空"
                )

                return ConfigUtil.read_env(
                    environment_name
                )

            # 当前用例的variables优先于extract.yaml。
            if variable_name in variables:
                return variables[variable_name]

            # setup提取的运行时变量从extract.yaml读取。
            return read_yaml(variable_name)

        return data