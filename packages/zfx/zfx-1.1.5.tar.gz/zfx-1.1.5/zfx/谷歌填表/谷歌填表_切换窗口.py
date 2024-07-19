def 谷歌填表_切换窗口(驱动器对象, 窗口名称, 异常返回=False):
    """
    切换到指定名称的窗口。

    参数:
        - 驱动器对象: 驱动器对象。
        - 窗口名称: 要切换到的窗口的名称。
        - 异常返回 (bool, optional): 如果为 True，出现异常时返回异常信息；如果为 False，出现异常时返回 False。默认值为 False。

    返回:
        - bool 或 str: 成功返回 True。如果请求失败且异常返回为 True，则返回异常信息；否则返回 False。
    """
    try:
        驱动器对象.switch_to.window(窗口名称)
        return True
    except Exception as e:
        if 异常返回:
            return str(f"处理失败: {e}")
        return False
