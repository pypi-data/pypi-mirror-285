import math


def 算数_求最大公约数(a, b):
    """
    计算两个数的最大公约数。

    参数:
        - a (int): 第一个整数。
        - b (int): 第二个整数。

    返回:
        - 最大公约数 (int): 两个数的最大公约数。
    """
    try:
        最大公约数 = math.gcd(a, b)
        return 最大公约数
    except Exception as e:
        print(f"计算最大公约数时发生错误: {e}")
        return None