def 列表_反转(列表):
    """
    反转列表中的元素顺序。

    参数:
        - 列表 (list): 要反转的列表。

    返回:
        - list: 反转后的列表。如果出现异常，返回原始列表。
    """
    try:
        return 列表[::-1]
    except Exception:
        return 列表