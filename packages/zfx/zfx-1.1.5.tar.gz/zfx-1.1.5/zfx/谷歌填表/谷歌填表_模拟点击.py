def 谷歌填表_模拟点击(驱动器对象, 元素对象):
    """
    模拟点击元素对象。

    参数:
        - 驱动器对象: WebDriver 对象，用于执行 JavaScript 脚本。
        - 元素对象: 要模拟点击的 WebElement 对象。

    返回:
        - bool: 成功返回 True，失败返回 False。
    """
    try:
        驱动器对象.execute_script("arguments[0].click();", 元素对象)
        return True
    except Exception:
        return False