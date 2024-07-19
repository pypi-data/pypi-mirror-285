def excel_保存Excel文件(表格对象, 文件路径):
    """
    参数:
    - 表格对象: 要保存的 Excel 文件的表格对象
    - 文件路径: 要保存的文件路径

    返回值:
    - 如果成功保存文件，则返回 True ；如果保存失败，则返回 False
    """
    try:
        表格对象.save(filename=文件路径)
        return True
    except Exception:
        return False