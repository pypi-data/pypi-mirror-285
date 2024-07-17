import psutil
import datetime


def 进程_取进程启动时间(pid):
    """
    根据进程ID获取进程的启动时间。

    参数:
        - pid (int): 要查询的进程ID。

    返回值:
        - str: 成功返回进程启动时间的字符串表示，失败返回空字符串。

    使用示例:
    启动时间 = 进程_取进程启动时间(1234)
    """
    try:
        process = psutil.Process(pid)
        start_time = process.create_time()
        return datetime.datetime.fromtimestamp(start_time).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return ""