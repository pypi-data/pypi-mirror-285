def 列表_去除前后空格(列表):
    """
    去除列表中每个字符串元素的前后空格。

    参数:
        - 列表 (list): 要处理的列表。

    返回:
        - list: 去除前后空格后的新列表。如果出现异常，返回原始列表。
    """
    try:
        # 使用列表推导式去除每个字符串元素的前后空格
        新列表 = [元素.strip() if isinstance(元素, str) else 元素 for 元素 in 列表]
        return 新列表
    except Exception:
        return 列表