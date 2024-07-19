def 谷歌填表_执行JavaScript(驱动器对象, 脚本, *参数):
    """
    执行 JavaScript 脚本。

    参数:
        - 驱动器对象: WebDriver 对象。
        - 脚本: 要执行的 JavaScript 脚本。
        - *参数: 传递给 JavaScript 脚本的参数。

    返回:
        - 执行 JavaScript 脚本后的返回值。失败返回 None。
    """
    try:
        return 驱动器对象.execute_script(脚本, *参数)
    except Exception:
        return None