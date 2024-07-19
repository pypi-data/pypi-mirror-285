import subprocess


def 模块_重置Winsock():
    """
    调用 'netsh winsock reset' 命令以重置 Winsock。
    """
    try:
        # 运行 netsh winsock reset 命令
        result = subprocess.run(['netsh', 'winsock', 'reset'], capture_output=True, text=True, check=True)

        # 打印命令的输出
        print("命令输出:")
        print(result.stdout)

        # 如果有错误输出，打印错误输出
        if result.stderr:
            print(result.stderr)

        print("Winsock 重置成功，请重启计算机以使更改生效。")
    except Exception:
        print(f"命令执行失败")