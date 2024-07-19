def 算数_求平均值(数值列表):
    """
    计算一组数的平均值。

    参数:
        - 数值列表 (list): 要计算平均值的数值列表。

    返回:
        - 平均值 (float): 数值列表的平均值。
    """
    try:
        平均值 = sum(数值列表) / len(数值列表)
        return 平均值
    except Exception as e:
        print(f"计算平均值时发生错误: {e}")
        return None