def excel_关闭Excel文件(表格对象):
    """
    参数:
    - 表格对象: 要关闭的 Excel 文件的表格对象

    返回值:
    - 如果成功关闭文件，则返回 True ；如果关闭失败，则返回 False

    使用提示：
    - 注意，如果修改内容之后直接调用此命令关闭表格，修改的内容不会进行保存。
    """
    try:
        表格对象.close()
        return True
    except Exception:
        return False