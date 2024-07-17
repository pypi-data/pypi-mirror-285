def 算数_求次方(基数, 指数):
    """
    计算基数的指定次方。

    参数:
        - 基数 (int or float): 要进行幂运算的基数。
        - 指数 (int or float): 要进行幂运算的指数。

    返回:
        - 数字 (int or float): 计算结果，即基数的指定次方。如果输入无效或出现异常，返回 None 并打印错误信息。

    使用示例:
        result = 算数_求次方(2, 3)
        print(result)  # 输出结果为 8

        result = 算数_求次方(2.5, 2)
        print(result)  # 输出结果为 6.25
    """
    try:
        result = 基数 ** 指数
        return result
    except Exception as e:
        print(f"计算次方时发生错误: {e}")
        return None