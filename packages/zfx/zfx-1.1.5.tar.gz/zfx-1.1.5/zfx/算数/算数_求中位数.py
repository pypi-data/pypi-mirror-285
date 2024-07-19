def 算数_求中位数(数值列表):
    """
    计算一组数的中位数。

    参数:
        - 数值列表 (list): 要计算中位数的数值列表。

    返回:
        - 中位数 (float): 数值列表的中位数。
    """
    try:
        数值列表.sort()
        n = len(数值列表)
        if n % 2 == 0:
            中位数 = (数值列表[n//2 - 1] + 数值列表[n//2]) / 2
        else:
            中位数 = 数值列表[n//2]
        return 中位数
    except Exception as e:
        print(f"计算中位数时发生错误: {e}")
        return None