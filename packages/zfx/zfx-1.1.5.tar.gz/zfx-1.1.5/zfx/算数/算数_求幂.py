import math


def 算数_求幂(基数, 指数):
    """
    计算给定数值的幂。

    参数:
        - 基数 (float): 要计算的基数。
        - 指数 (float): 要计算的指数。

    返回:
        - 幂值 (float): 给定数值的幂。
    """
    try:
        幂值 = math.pow(基数, 指数)
        return 幂值
    except Exception as e:
        print(f"计算幂值时发生错误: {e}")
        return None