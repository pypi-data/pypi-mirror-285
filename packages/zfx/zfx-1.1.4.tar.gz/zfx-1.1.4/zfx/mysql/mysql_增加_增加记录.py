def mysql_增加_增加记录(连接对象, 表名, 数据字典):
    """
    向数据库表中插入新记录。

    参数：
        - 连接对象: 数据库连接对象。
        - 表名: 要插入新记录的表的名称，字符串类型。
        - 值字典: 插入的字段及其对应的值，字典类型。例如 {"username": "jack", "password": "jack@126.com"}。

    返回值：
        - 执行成功返回 True，失败返回 False。

    使用示例：
    值字典 = {"username": "jack", "password": "jack@126.com", "nua": 123}
    插入结果 = 数据库_mysql_增加记录(连接对象, "asida", 值字典)
    """
    try:
        # 构建插入语句
        列名 = ', '.join(数据字典.keys())
        占位符 = ', '.join(['%s'] * len(数据字典))
        插入语句 = f"INSERT INTO {表名} ({列名}) VALUES ({占位符})"

        # 执行插入操作
        游标 = 连接对象.cursor()
        游标.execute(插入语句, list(数据字典.values()))

        # 提交事务
        连接对象.commit()

        # 关闭游标
        游标.close()

        return True
    except Exception:
        return False