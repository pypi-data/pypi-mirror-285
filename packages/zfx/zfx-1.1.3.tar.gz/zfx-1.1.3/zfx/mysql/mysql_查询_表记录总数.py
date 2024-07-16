def mysql_查询_表记录总数(游标, 表名):
    """
    查询指定表的记录数量。

    参数：
        - 游标: 数据库游标对象。
        - 表名: 要查询记录数量的表名。

    返回值：
        - 返回指定表的记录数量，如果查询失败返回 None。
    """
    try:
        # 构建查询语句
        查询语句 = f"SELECT COUNT(*) FROM {表名}"

        # 执行查询操作
        游标.execute(查询语句)

        # 获取记录数量
        记录数 = 游标.fetchone()[0]

        return 记录数
    except Exception:
        return None