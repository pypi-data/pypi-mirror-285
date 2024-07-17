import psutil


def 进程_名取ID列表(进程名):
    """
    根据进程名称获取所有匹配的进程ID列表。

    参数:
        - 进程名 (str): 要查询的进程名称，包括后缀（例如：chrome.exe）。

    返回值:
        - list: 成功找到返回包含所有匹配进程ID的列表，失败返回空列表。

    使用示例:
    进程ID列表 = 进程_名取ID列表("chrome.exe")
    """
    try:
        pid_list = []
        # 遍历所有运行中的进程
        for proc in psutil.process_iter(['pid', 'name']):
            # 检查进程名称是否匹配
            if proc.info['name'] == 进程名:
                pid_list.append(proc.info['pid'])  # 将匹配的进程ID加入列表
        return pid_list  # 返回包含所有匹配进程ID的列表
    except Exception:
        return []  # 捕获所有异常并返回空列表