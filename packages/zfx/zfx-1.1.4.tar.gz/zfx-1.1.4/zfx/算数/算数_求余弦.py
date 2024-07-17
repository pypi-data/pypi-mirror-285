import math


def 算数_求余弦(角度):
    """
    计算给定角度的余弦值。

    参数:
        - 角度 (float): 要计算余弦值的角度，单位为度。

    返回:
        - 余弦值 (float): 给定角度的余弦值。如果输入无效或出现异常，返回 None 并打印错误信息。

    # 示例用法
    angle = 60
    cos_value = 算数_求余弦(angle)
    print(f"{angle}度的余弦值为: {cos_value}")
    """
    try:
        # 将角度转换为弧度
        弧度 = math.radians(角度)

        # 计算余弦值
        余弦值 = math.cos(弧度)

        return 余弦值
    except Exception:
        return None