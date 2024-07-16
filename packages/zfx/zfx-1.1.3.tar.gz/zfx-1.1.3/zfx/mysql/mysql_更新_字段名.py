def mysql_更新_字段名(连接对象, 表名, 新字段名列表):
    """
    更新指定表的字段名，记住列表成员数量必须和MySQL表单字段数量一致才行。

    参数：
        - 连接对象：MySQL 数据库连接对象。
        - 表名：要更新字段名的表名称。
        - 新字段名列表：新的字段名称列表，依次更新字段名。

    返回值：
        - 更新成功返回 True，失败返回 False。
    """
    try:
        cursor = 连接对象.cursor()

        # 获取当前字段名称、类型、字符集和排序规则
        查询字段名语句 = f"SHOW FULL COLUMNS FROM {表名}"
        cursor.execute(查询字段名语句)
        结果 = cursor.fetchall()
        当前字段名列表 = [行[0] for 行 in 结果]

        # 检查新字段名列表长度是否匹配
        if len(当前字段名列表) != len(新字段名列表):
            print("新字段名列表长度与当前字段数量不匹配。")
            return False

        # 依次更新字段名
        for 行 in 结果:
            旧字段名 = 行[0]
            新字段名 = 新字段名列表[当前字段名列表.index(旧字段名)]
            字段类型 = 行[1]
            排序规则 = 行[2]  # 提取排序规则

            # 处理可能的排序规则
            if 排序规则 and not 排序规则.isdigit() and 排序规则 not in ['PRI', 'UNI', 'MUL']:
                更新字段名语句 = f"ALTER TABLE {表名} CHANGE `{旧字段名}` `{新字段名}` {字段类型} COLLATE {排序规则}"
            else:
                更新字段名语句 = f"ALTER TABLE {表名} CHANGE `{旧字段名}` `{新字段名}` {字段类型}"

            try:
                cursor.execute(更新字段名语句)
                print(f"字段名 '{旧字段名}' 成功更新为 '{新字段名}'")
            except Exception as e:
                print(f"更新字段 '{旧字段名}' 到 '{新字段名}' 失败: {e}")
                return False

        连接对象.commit()
        return True

    except Exception as e:
        print(f"发生错误: {e}")
        return False