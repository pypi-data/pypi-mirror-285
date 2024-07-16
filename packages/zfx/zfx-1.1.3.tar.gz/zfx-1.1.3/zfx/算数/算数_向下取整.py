import math

def 算数_向下取整(数字):
    """
    向下取整函数，返回不大于给定数字的最大整数。

    参数:
        数字 (float): 需要向下取整的数字。

    返回:
        int: 不大于给定数字的最大整数。如果失败则返回 False。

    使用示例:
        print(算数_向下取整(3.8))  # 输出：3
        print(算数_向下取整(-3.8))  # 输出：-4
    """
    try:
        return math.floor(数字)
    except Exception:
        return False