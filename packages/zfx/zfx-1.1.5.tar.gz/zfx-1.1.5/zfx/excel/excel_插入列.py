def excel_插入列(表格对象, 工作表名, 列号, 列数=1):
    """
    参数:
    - 表格对象: 要操作的表格对象
    - 工作表名: 要插入列的工作表名称
    - 列号: 要插入列的位置
    - 列数: 要插入的列数，默认为1

    返回值:
    - 如果成功插入列，则返回 True；如果插入失败，则返回 False

    使用示例：
    - zfxtest.excel_插入列(表格对象, "Sheet1", 2, 1)
    """
    try:
        # 获取指定的工作表
        工作表 = 表格对象[工作表名]
        # 插入指定列数
        工作表.insert_cols(列号, 列数)
        return True
    except Exception:
        return False