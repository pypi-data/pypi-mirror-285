def mysql_更新_指定字段空值填充(连接对象, 表名, 字段名, 填充数据):
    """
    填充某个字段的空值（NULL 或空字符串）。

    参数：
        - 连接对象: 数据库连接对象。
        - 表名: 需要更新的表的名称。
        - 字段名: 需要填充空值的字段名称。
        - 填充数据: 用于填充的值，可以是字符串或数值。

    返回值：
        - 更新成功返回 True，失败返回 False。
    """
    游标 = None
    try:
        # 构造完整的更新 SQL 语句，将字段的空值替换为填充值
        sql = f"UPDATE {表名} SET {字段名} = '{填充数据}' WHERE {字段名} IS NULL OR {字段名} = '';"

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