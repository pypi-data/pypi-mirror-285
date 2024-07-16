import math


def 算数_求平方根(数字):
    """
    计算给定数字的平方根。

    参数:
        - 数字: 要计算平方根的数字。

    返回:
        - 数字，给定数字的平方根。如果输入无效或出现异常，返回 None 并打印错误信息。

    # 调用示例
    result = 求平方根(16)
    print(result)  # 输出结果为 4.0


    """
    try:
        result = math.sqrt(数字)
        return result
    except Exception as e:
        print(f"计算平方根时发生错误: {e}")
        return None