def 列表_排序(列表, 逆序=False):
    """
    返回排序后的列表。

    参数:
        列表 (list): 要排序的列表。
        逆序 (bool): 是否逆序排序，默认False（升序）。

    返回:
        list: 排序后的列表。

    示例:
        排序后的列表 = 列表_排序([3, 1, 2])
        if 排序后的列表 is not None:
            print("排序后的列表:", 排序后的列表)
        else:
            print("排序失败")
    """
    try:
        return sorted(列表, reverse=逆序)
    except Exception:
        return None