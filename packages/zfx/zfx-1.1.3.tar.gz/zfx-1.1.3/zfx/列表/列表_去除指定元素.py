def 列表_去除指定元素(列表, 元素):
    """
    返回去除指定元素后的列表。

    参数:
        列表 (list): 原始列表。
        元素 (any): 要去除的元素。

    返回:
        list: 去除指定元素后的列表。

    示例:
        新列表 = 列表_去除指定元素([1, 2, 3, 2], 2)
        if 新列表 is not None:
            print("去除指定元素后的列表:", 新列表)
        else:
            print("去除指定元素失败")
    """
    try:
        return [x for x in 列表 if x != 元素]
    except Exception:
        return None