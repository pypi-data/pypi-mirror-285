from openpyxl.styles import Alignment


def excel_设置单元格格式(表格对象, 工作表名, 单元格, 对齐=None):
    """
    参数:
        - 表格对象: 要操作的表格对象
        - 工作表名: 要设置单元格格式的工作表名称
        - 单元格: 要设置格式的单元格坐标，例如 'A1'
        - 对齐: 对齐方式，可选值为 "左对齐"、"右对齐"、"居中对齐"

    返回值:
    - 如果成功设置单元格格式，则返回 True；如果设置失败，则返回 False，并打印错误信息
    """
    try:
        工作表 = 表格对象[工作表名]
        单元格对象 = 工作表[单元格]
        if 对齐:
            对齐方式 = {
                "左对齐": "left",
                "右对齐": "right",
                "居中对齐": "center"
            }
            if 对齐 in 对齐方式:
                单元格对象.alignment = Alignment(horizontal=对齐方式[对齐])
            else:
                print(f"无效的对齐方式: {对齐}")
                return False
        return True
    except Exception as e:
        print(f"设置单元格格式时发生错误: {e}")
        return False
