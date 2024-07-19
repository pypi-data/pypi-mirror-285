def mysql_更新_置字段所有数据为Null(连接对象, 表名, 字段):
    """
    将指定字段的所有数据置为 NULL。

    参数：
        - 连接对象: 数据库连接对象。
        - 表名: 需要更新的表的名称。
        - 字段: 需要置为 NULL 的字段名称。

    返回值：
        - 更新成功返回 True，失败返回 False。
    """
    游标 = None
    try:
        # 构造完整的更新 SQL 语句，将字段值置为 NULL
        sql = f"UPDATE {表名} SET {字段} = NULL;"

        # 获取游标对象，用于执行 SQL 语句
        游标 = 连接对象.cursor()
        # 执行 SQL 语句
        游标.execute(sql)
        # 提交事务，确保更改生效
        连接对象.commit()
        return True
    except Exception:
        return False
    finally:
        # 如果游标对象存在，关闭游标，释放资源
        if 游标:
            游标.close()