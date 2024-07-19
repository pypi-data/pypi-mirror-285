def 谷歌填表_切换框架(驱动器对象, 框架引用, 异常返回=False):
    """
    切换到指定的框架。

    参数:
        - 驱动器对象: 驱动器对象。
        - 框架引用: 要切换到的框架的引用，可以是名称、索引或 WebElement 对象。
        - 异常返回 (bool, optional): 如果为 True，出现异常时返回异常信息；如果为 False，出现异常时返回 False。默认值为 False。

    返回:
        - bool 或 str: 成功返回 True。如果请求失败且异常返回为 True，则返回异常信息；否则返回 False。
    """
    try:
        驱动器对象.switch_to.frame(框架引用)
        return True
    except Exception as e:
        if 异常返回:
            return str(f"处理失败: {e}")
        return False