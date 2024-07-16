def 谷歌填表_保存截图(驱动器对象, 文件名, 异常返回=False):
    """
    保存当前页面的截图。

    参数:
        - 驱动器对象: 驱动器对象。
        - 文件名: 要保存的截图文件的名称。
        - 异常返回 (bool, optional): 如果为 True，出现异常时返回异常信息；如果为 False，出现异常时返回 False。默认值为 False。

    返回:
        - bool 或 str: 成功返回 True。如果请求失败且异常返回为 True，则返回异常信息；否则返回 False。
    """
    try:
        驱动器对象.save_screenshot(文件名)
        return True
    except Exception as e:
        if 异常返回:
            return str(f"处理失败: {e}")
        return False