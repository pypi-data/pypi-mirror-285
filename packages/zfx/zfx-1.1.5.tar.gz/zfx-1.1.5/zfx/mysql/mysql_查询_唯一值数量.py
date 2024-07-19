def mysql_查询_唯一值数量(连接对象, 表名, 字段名):
    """
    查询指定表中特定字段的唯一值数量。

    参数：
        - 连接对象：与数据库的连接对象。
        - 表名：要查询的表名。
        - 字段名：要查询的字段名。

    返回值：
        - 唯一值数量：字段中唯一值的数量，如果查询失败则返回 None。
    """
    游标对象 = None
    try:
        游标对象 = 连接对象.cursor()
        游标对象.execute(f"SELECT COUNT(DISTINCT {字段名}) FROM {表名}")
        唯一值数量 = 游标对象.fetchone()[0]
        return 唯一值数量
    except Exception:
        return None
    finally:
        if 游标对象:
            游标对象.close()