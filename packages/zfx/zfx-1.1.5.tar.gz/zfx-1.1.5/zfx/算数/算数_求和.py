def 算数_求和(数值列表):
    """
    计算一组数的和。

    参数:
        - 数值列表 (list): 要计算和的数值列表。

    返回:
        - 和 (float): 数值列表的和。
    """
    try:
        和 = sum(数值列表)
        return 和
    except Exception as e:
        print(f"计算和时发生错误: {e}")
        return None