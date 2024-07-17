def mysql_删除记录(连接, 表名, 条件):
    """
    删除符合条件的记录。

    参数：
        - 连接: 数据库连接对象。
        - 表名：要进行删除操作的表的名称。
        - 条件：删除符合条件的记录的条件。如果为''(空字符串)，则删除所有记录。

    返回值：
        - 删除成功返回 True，失败返回 False。

    使用示例
    删除结果 = 数据库_mysql_删除记录(连接对象,  "asida", "username='jack'")
    删除结果 = 数据库_mysql_删除记录(连接对象,  "asida", "id > 5")
    """
    try:
        # 构建删除语句
        删除语句 = f"DELETE FROM {表名}"
        if 条件:
            删除语句 += f" WHERE {条件}"

        # 执行删除操作
        连接.cursor().execute(删除语句)

        # 提交事务
        连接.commit()

        return True
    except Exception:
        return False