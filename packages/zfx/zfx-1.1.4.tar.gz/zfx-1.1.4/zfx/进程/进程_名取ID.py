import psutil

def 进程_名取ID(进程名):
    """
    根据进程名称获取进程ID。

    参数:
        - 进程名 (str): 要查询的进程名称，包括后缀（例如：chrome.exe）。

    返回值:
        - int: 成功找到返回进程ID，失败返回0。

    使用示例:
    进程ID = 进程_名取ID("chrome.exe")
    """
    try:
        # 遍历所有运行中的进程
        for proc in psutil.process_iter(['pid', 'name']):
            # 检查进程名称是否匹配
            if proc.info['name'] == 进程名:
                return proc.info['pid']  # 返回找到的进程ID
        return 0  # 没有找到匹配的进程名，返回0
    except Exception:
        return 0  # 捕获所有异常并返回0
