import subprocess
import os
import tempfile


def 文件_封装Py代码成EXE_独立编译(脚本路径):
    """
    将指定的 Python 脚本打包成可执行的 EXE 文件，并将输出文件保存到桌面。

    参数:
    脚本路径 (str): 要打包的 Python 脚本的路径。该路径应指向一个有效的 Python 脚本文件。

    返回值:
    无

    异常:
    subprocess.CalledProcessError: 如果打包过程中出现错误，将会抛出 CalledProcessError 异常。

    注意:
    - 该函数将指定的 Python 脚本进行封装，将其转换为可执行的 EXE 文件。
    - 封装后的 EXE 文件将会保存在用户的桌面上。

    # 使用示例
    - 文件_封装Py代码成EXE_独立编译(py源码路径)
    """
    try:
        # 获取系统桌面的路径
        桌面路径 = os.path.join(os.path.expanduser("~"), 'Desktop')

        # 创建一个临时目录
        with tempfile.TemporaryDirectory() as 临时目录:
            # 使用 subprocess.run 调用 pyinstaller 命令，将脚本打包成单个 EXE 文件，并指定输出目录为桌面
            subprocess.run(['pyinstaller', '--onefile', '--distpath', 桌面路径, '--workpath', 临时目录, '--specpath', 临时目录, 脚本路径], check=True)

        print(f"成功将 {脚本路径} 打包成 EXE 文件，并保存在桌面。")  # 打包成功后输出提示信息
    except subprocess.CalledProcessError as e:
        # 如果打包过程中发生错误，捕获异常并输出错误信息
        print(f"打包过程中出现错误: {e}")