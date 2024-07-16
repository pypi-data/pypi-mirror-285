def mysql_创建新表(连接对象, 表名, 结构信息):
    """
    根据给定的表结构信息创建新表。

    参数：
        - 连接对象：MySQL 数据库连接对象。
        - 表名：要创建的新表的名称。
        - 结构信息：包含每个字段的详细信息字典列表，包括字段名、数据类型、长度、是否允许为空、是否为主键和是否自增。

    返回值：
        - 创建成功返回 True，失败返回 False。
    """
    try:
        cursor = 连接对象.cursor()

        # 构建 CREATE TABLE 语句
        创建语句 = f"CREATE TABLE IF NOT EXISTS {表名} ("

        for 字段信息 in 结构信息:
            字段名 = 字段信息["字段名"]
            数据类型 = 字段信息["数据类型"]
            长度 = 字段信息["长度"]
            是否允许为空 = "NULL" if 字段信息["是否允许为空"] == "YES" else "NOT NULL"
            是否主键 = "PRIMARY KEY" if 字段信息["是否主键"] else ""
            是否自增 = "AUTO_INCREMENT" if 字段信息["是否自增"] else ""
            长度部分 = f"({长度})" if 长度 else ""

            创建语句 += f"{字段名} {数据类型}{长度部分} {是否允许为空} {是否主键} {是否自增}, "

        创建语句 = 创建语句.rstrip(", ") + ")"

        # 执行创建表操作
        cursor.execute(创建语句)
        连接对象.commit()
        return True

    except Exception:
        return False