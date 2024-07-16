import math


def 算数_求最小公倍数(a, b):
    """
    计算两个数的最小公倍数。

    参数:
        - a (int): 第一个整数。
        - b (int): 第二个整数。

    返回:
        - 最小公倍数 (int): 两个数的最小公倍数。
    """
    try:
        最小公倍数 = abs(a * b) // math.gcd(a, b)
        return 最小公倍数
    except Exception as e:
        print(f"计算最小公倍数时发生错误: {e}")
        return None