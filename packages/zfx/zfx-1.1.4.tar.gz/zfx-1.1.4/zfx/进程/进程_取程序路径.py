import psutil


def 进程_取程序路径(pid):
    """
    根据进程ID获取程序路径。

    参数:
        - pid (int): 要查询的进程ID。

    返回值:
        - str: 成功返回程序路径，失败返回空字符串。

    使用示例:
    程序路径 = 进程_取程序路径(1234)
    """
    try:
        process = psutil.Process(pid)
        return process.exe()
    except Exception as e:
        return ""