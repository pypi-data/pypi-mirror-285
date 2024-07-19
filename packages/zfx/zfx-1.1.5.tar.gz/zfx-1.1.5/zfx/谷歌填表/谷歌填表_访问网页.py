def 谷歌填表_访问网页(驱动器对象, 网址):
    """
    使用提供的驱动程序访问指定的网址。

    参数:
        - 驱动器对象: WebDriver 对象，用于控制浏览器的行为。
        - 网址: 要访问的网址。

    返回:
        - bool: 访问成功返回 True，访问失败返回 False。
    """
    try:
        驱动器对象.get(网址)
        return True
    except Exception:
        return False