import math


def 算数_求对数(值, 基数=math.e):
    """
    计算给定数值的对数。

    参数:
        - 值 (float): 要计算对数的数值。
        - 基数 (float): 对数的基数，默认是自然对数的基数e。

    返回:
        - 对数值 (float): 给定数值的对数。
    """
    try:
        对数值 = math.log(值, 基数)
        return 对数值
    except Exception as e:
        print(f"计算对数值时发生错误: {e}")
        return None