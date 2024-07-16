import math


def 算数_求余弧度(值):
    """
    计算反余弦、反正弦、反正切的值，返回结果为弧度。

    参数:
        - 值 (float): 要计算的数值。

    返回:
        - 余弧度值 (dict): 包含反余弦、反正弦、反正切的值。
    """
    try:
        反余弦 = math.acos(值)
        反正弦 = math.asin(值)
        反正切 = math.atan(值)
        return {
            "反余弧度": 反余弦,
            "反正弧度": 反正弦,
            "反正切弧度": 反正切
        }
    except Exception as e:
        print(f"计算余弧度值时发生错误: {e}")
        return None