import subprocess
import sys
import os


def 模块_更新到指定版本2(version):
    """
    更新名为 zfx 的 Python 模块到指定版本。

    参数:
        version (str): 要更新到的版本号。

    返回:
        bool: 如果更新成功，则返回True，否则返回False。

    示例:
        zfx.模块_更新到指定版本2()
    """
    try:
        # 获取当前Python解释器的目录
        python_dir = os.path.dirname(sys.executable)
        pip_path = os.path.join(python_dir, 'Scripts', 'pip.exe')

        # 使用subprocess模块执行固定的命令
        subprocess.run([pip_path, "install", "--upgrade", f"zfx=={version}"], check=True)
        return True
    except Exception:
        return False  # 捕获其他所有异常并返回 False