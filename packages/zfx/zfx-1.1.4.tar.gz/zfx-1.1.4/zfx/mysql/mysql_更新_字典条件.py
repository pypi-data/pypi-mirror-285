def mysql_更新_字典条件(连接, 表名, 值字典, 条件字典=None):
    """
    更新指定字段的数据。

    参数：
        - 连接: 数据库连接对象。
        - 表名：要更新数据的表的名称。
        - 值字典：要更新的字段及其对应的值，字典类型。例如 {"字段1": "值1", "字段2": "值2", "字段3": 1234}。
        - 条件字典：查找符合条件的记录的条件，字典类型。例如 {"id": 1, "name": "Jack"}。如果为空字典或为 None，则更新所有记录。

    返回值：
        - 更新成功返回 True，失败返回 False。
    """
    try:
        # 构建更新语句
        赋值语句 = ', '.join([f"{字段}=%s" for 字段 in 值字典.keys()])
        更新语句 = f"UPDATE {表名} SET {赋值语句}"

        # 如果有条件，则添加条件到更新语句中
        if 条件字典:
            条件语句 = ' AND '.join([f"{字段}=%s" for 字段 in 条件字典.keys()])
            更新语句 += f" WHERE {条件语句}"

        # 提取值列表
        值列表 = list(值字典.values())
        if 条件字典:
            值列表.extend(list(条件字典.values()))

        # 执行更新操作
        连接.cursor().execute(更新语句, 值列表)

        # 提交事务
        连接.commit()

        return True
    except Exception:
        return False