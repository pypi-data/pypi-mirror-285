from openpyxl import load_workbook


def excel_打开Excel文件(文件路径):
    """
    参数:
    - 文件路径: 要打开的 Excel 文件的路径(只支持xlsx后缀)

    返回值:
    - 如果成功打开文件，则返回 表格对象；如果文件打开失败，则返回 None

    使用提示：
    - 在文件被占用时，此函数无法获得操作权限，则会打开失败，返回None
    """
    try:
        return load_workbook(filename=文件路径)
    except Exception:
        return None