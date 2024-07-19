def mysql_更新_SQL语句条件(连接对象, 表名, 值字典, 条件):
    """
    根据条件更新 MySQL 数据库表中的记录。

    参数：
        - 连接对象: 数据库连接对象。
        - 表名(字符串): 需要更新的表的名称。
        - 更新字段和值(字典): 要更新的字段及其对应的值，字典类型。例如 {"字段1": "值1", "字段2": "值2"}。
        - 条件(字符串): 用于筛选需要更新记录的条件，字符串类型。例如 "id = 1 AND name = 'Jack'"。

    返回值：
        - 更新成功返回 True，失败返回 False。
    """
    游标 = None
    try:
        # 生成更新字段和值的 SQL 片段
        # 使用列表解析将字典转换为 "字段 = '值'" 的形式，并用逗号分隔
        更新片段 = ", ".join([f"{字段} = '{值}'" for 字段, 值 in 值字典.items()])

        # 构造完整的更新 SQL 语句
        # 格式为：UPDATE 表名 SET 更新片段 WHERE 条件;
        sql = f"UPDATE {表名} SET {更新片段} WHERE {条件};"

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