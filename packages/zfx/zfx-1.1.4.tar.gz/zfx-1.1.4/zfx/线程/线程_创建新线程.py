import threading


def 线程_创建新线程(目标函数, 线程名称=None, *参数):
    """
    创建一个新线程并启动。

    参数:
        目标函数 (callable): 线程要执行的目标函数
        线程名称 (str, optional): 线程的名称，默认为 None
        *参数: 传递给目标函数的参数

    返回:
        threading.Thread: 创建的线程对象，如果创建失败则返回 None
    """
    try:
        线程 = threading.Thread(target=目标函数, args=参数, name=线程名称)
        线程.start()
        return 线程
    except Exception:
        return None