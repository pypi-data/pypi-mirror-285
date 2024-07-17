def 算数_取绝对值(数值):
    """
    取绝对值函数，返回给定数值的绝对值。

    参数:
        - 数值 (int or float): 需要取绝对值的数值。

    返回:
        - int or float: 给定数值的绝对值。如果输入无效或出现异常，返回 None 并打印错误信息。

    使用示例:
        结果 = 算数_取绝对值(5)  # 输出：5
        结果2 = 算数_取绝对值(-3)  # 输出：3
    """
    try:
        if 数值 >= 0:
            return 数值
        else:
            return -数值
    except Exception as e:
        print(f"取绝对值时发生错误: {e}")
        return None