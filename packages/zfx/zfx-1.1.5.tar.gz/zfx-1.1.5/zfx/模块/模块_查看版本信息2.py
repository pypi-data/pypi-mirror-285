import subprocess
import sys
import os


def 模块_查看版本信息2():
    """
    查看模块 zfx 的版本号，及简介。

    返回:
        str: 模块 zfx 的版本号，如果模块不存在或发生异常，则打印失败信息。

    示例:
        zfx.模块_查看版本信息2()
    """
    try:
        # 获取当前Python解释器的目录
        python_dir = os.path.dirname(sys.executable)
        pip_path = os.path.join(python_dir, 'Scripts', 'pip.exe')

        # 使用subprocess模块执行固定的命令
        subprocess.run([pip_path, "show", "zfx"], check=True)
    except Exception:
        print(f"版本信息获取失败，请稍后再试")