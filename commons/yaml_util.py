import os
import yaml

# 可以用这种方法代替类变量这一中间变量
# 写入：追加
def write_yaml(data):
    with open(os.getcwd()+"/extract.yaml", encoding="utf-8", mode="a+") as f:
        yaml.dump(data, stream=f, allow_unicode=True)

# 读取
def read_yaml(key):
    with open(os.getcwd()+"/extract.yaml", encoding="utf-8", mode="r") as f:
        value = yaml.load(f, yaml.FullLoader)
        return value[key]

# 清空
def clear_yaml():
    with open(os.getcwd()+"/extract.yaml", encoding="utf-8", mode="w") as f:
        f.truncate()

# 读取测试用例
def read_yaml_testcase(yamlpath):
    with open(os.getcwd() + "/" + yamlpath, encoding="utf-8", mode="r") as f:
        value = yaml.load(f, yaml.FullLoader)
        return value