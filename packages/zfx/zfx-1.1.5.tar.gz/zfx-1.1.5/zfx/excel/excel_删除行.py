def excel_删除行(表格对象, 工作表名, 行号):
    """
    参数:
    - 表格对象: 要操作的表格对象
    - 工作表名: 要删除行的工作表名称
    - 行号: 要删除的行号

    返回值:
    - 如果成功删除行，则返回 True；如果删除失败，则返回 False
    """
    try:
        工作表 = 表格对象[工作表名]
        工作表.delete_rows(行号)
        return True
    except Exception:
        return False