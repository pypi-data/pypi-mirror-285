import csv


def mysql_查询_导出数据表(连接对象, 表名, 文件路径):
    """
    导出整个表的数据到本地文件（例如 CSV 文件）不建议大表使用，会等待很久。

    参数：
        - 连接对象: 数据库连接对象。
        - 表名: 需要导出的表的名称。
        - 文件路径: 导出文件的本地路径（例如 '数据.csv'）。

    返回值：
        - 导出成功返回 True，失败返回 False。
    """
    游标 = None
    try:
        # 获取游标对象，用于执行 SQL 查询
        游标 = 连接对象.cursor()
        # 执行查询语句，获取所有数据
        游标.execute(f"SELECT * FROM {表名};")
        结果 = 游标.fetchall()

        # 获取表的列名
        列名 = [i[0] for i in 游标.description]

        # 将数据写入 CSV 文件
        with open(文件路径, 'w', newline='', encoding='utf-8') as 文件:
            写入器 = csv.writer(文件)
            写入器.writerow(列名)
            写入器.writerows(结果)

        return True
    except Exception:
        return False
    finally:
        # 如果游标对象存在，关闭游标，释放资源
        if 游标:
            游标.close()