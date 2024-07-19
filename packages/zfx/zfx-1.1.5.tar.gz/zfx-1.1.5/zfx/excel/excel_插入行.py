def excel_插入行(表格对象, 工作表名, 行号):
    """
    参数:
    - 表格对象: 要操作的表格对象
    - 工作表名: 要插入行的工作表名称
    - 行号: 要插入行的行号

    返回值:
    - 如果成功插入行，则返回 True；如果插入失败，则返回 False
    """
    try:
        工作表 = 表格对象[工作表名]
        工作表.insert_rows(行号)
        return True
    except Exception:
        return False