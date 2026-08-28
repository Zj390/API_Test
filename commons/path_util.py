from pathlib import Path


# 当前文件位于 commons 目录，向上两层就是项目根目录。
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# extract.yaml 无论从哪里运行测试，都固定在项目根目录。
EXTRACT_FILE = PROJECT_ROOT / "extract.yaml"


def get_project_path(relative_path):
    """将相对路径转换为基于项目根目录的绝对路径。"""
    return PROJECT_ROOT / relative_path