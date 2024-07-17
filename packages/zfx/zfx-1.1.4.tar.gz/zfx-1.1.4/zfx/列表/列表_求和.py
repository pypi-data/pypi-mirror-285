def 列表_求和(列表):
    """
    返回列表中所有元素的和。

    参数:
        列表 (list): 包含数字的列表。

    返回:
        数值: 列表中所有元素的和。

    示例:
        总和 = 列表_求和([1, 2, 3])
        if 总和 is not None:
            print("列表元素的和:", 总和)
        else:
            print("求和失败")
    """
    try:
        return sum(列表)
    except Exception:
        return None