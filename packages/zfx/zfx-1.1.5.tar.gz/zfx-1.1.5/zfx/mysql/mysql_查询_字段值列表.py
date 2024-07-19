def mysql_查询_字段值列表(连接对象, 表名, 字段名):
    """
    查询指定表中特定字段的值列表。

    参数：
        - 连接对象：与数据库的连接对象。
        - 表名：要查询的表名。
        - 字段名：要查询的字段名。

    返回值：
        - 字段值列表：包含所有值的列表，如果查询失败则返回 None。
    """
    游标对象 = None
    try:
        游标对象 = 连接对象.cursor()
        游标对象.execute(f"SELECT {字段名} FROM {表名}")
        字段值列表 = [row[0] for row in 游标对象.fetchall()]
        return 字段值列表
    except Exception:
        return None
    finally:
        if 游标对象:
            游标对象.close()