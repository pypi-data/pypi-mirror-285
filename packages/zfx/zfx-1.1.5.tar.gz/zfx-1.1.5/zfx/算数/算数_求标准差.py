import math


def 算数_求标准差(数值列表):
    """
    计算一组数的标准差。

    参数:
        - 数值列表 (list): 要计算标准差的数值列表。

    返回:
        - 标准差 (float): 数值列表的标准差。如果输入无效或出现异常，返回 None 并打印错误信息。
    """
    try:
        # 计算平均值
        平均值 = sum(数值列表) / len(数值列表)

        # 计算方差
        方差 = sum((x - 平均值) ** 2 for x in 数值列表) / len(数值列表)

        # 计算标准差
        标准差 = math.sqrt(方差)

        return 标准差
    except Exception as e:
        print(f"计算标准差时发生错误: {e}")
        return None