import math


def 算数_求阶乘(值):
    """
    计算给定整数的阶乘。

    参数:
        - 值 (int): 要计算的整数。

    返回:
        - 阶乘值 (int): 给定整数的阶乘。
    """
    try:
        阶乘值 = math.factorial(值)
        return 阶乘值
    except Exception as e:
        print(f"计算阶乘值时发生错误: {e}")
        return None