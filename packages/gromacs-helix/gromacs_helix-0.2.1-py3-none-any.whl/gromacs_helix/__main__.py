"""
启动模块化程序的脚本。

该脚本允许通过 `python -m` 模块化调用程序。
"""

from .main import app

# 通过指定 prog_name 参数来设置程序的名称，
# 这有助于生成更清晰、更专业的帮助信息和命令行提示。
app(prog_name="gromacs-helix")

# 区别：
# 默认用法提示 `python -m gromacs_helix [OPTIONS] COMMAND [ARGS]...`
# 优化后用法提示 `gromacs-helix [OPTIONS] COMMAND [ARGS]...`
