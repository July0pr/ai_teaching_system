# import sqlite3
#
# db_path = r"D:\项目与竞赛\agent_2\data\db.db"  # 确认路径
# conn = sqlite3.connect(db_path)
# cursor = conn.cursor()
#
# # 列出所有表
# cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
# tables = cursor.fetchall()
# print("Tables:", tables)
#
# # 如果有 users 表，执行查询
# if ('users',) in tables:
#     cursor.execute("SELECT * FROM users LIMIT 10")  # 获取 users 表中的前 10 行
#     print('users:')
#     rows = cursor.fetchall()
#     for row in rows:
#         print(row)
#
# # 如果有 class_students 表，执行查询
# if ('class_student',) in tables:
#     cursor.execute("SELECT * FROM class_student LIMIT 10")  # 获取 class_student 表中的前 10 行
#     print('students:')
#     rows = cursor.fetchall()
#     for row in rows:
#         print(row)
#
# conn.close()

# import sqlite3
#
# db_path = r"D:\项目与竞赛\agent_2\data\db.db"  # 确认路径
# conn = sqlite3.connect(db_path)
# cursor = conn.cursor()
#
# # 列出所有表
# cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
# tables = cursor.fetchall()
# print("Tables:", tables)
#
# # 检查 class_students 是否存在并查看内容
# if ('class_students',) in tables:
#     cursor.execute("SELECT COUNT(*) FROM class_students")
#     count = cursor.fetchone()[0]  # 获取行数
#     if count == 0:
#         print("class_students 表是空的")
#     else:
#         print(f"class_students 表中有 {count} 条记录")
#
#         # 查询前 10 条记录
#         cursor.execute("SELECT * FROM class_students LIMIT 10")
#         rows = cursor.fetchall()
#
#         # 打印字段名称
#         column_names = [description[0] for description in cursor.description]
#         print("字段名称:", column_names)
#
#         # 打印前 10 条数据
#         for row in rows:
#             print(row)
#
# conn.close()


import sqlite3

db_path = r"D:/项目与竞赛/深度学习与人工智能/agent_all/data/db.db"  # 确保路径正确
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 列出所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables:", [t[0] for t in tables])  # 输出所有表名

# 你要查询的表
target_tables = ["resources"]

# resource_id = 10
# new_file_path = r"D:\项目与竞赛\深度学习与人工智能\agent_all\data\教案\高二上学期教案.txt"
#
# cursor.execute("""
#     UPDATE resources
#     SET file_path = ?
#     WHERE id = ?;
# """, (new_file_path, resource_id))


# # 提交更改
# conn.commit()

# print(f"Updated record with ID {resource_id}")

# 查询每个表的字段信息，并检查表是否为空
for table in target_tables:
    cursor.execute(f"PRAGMA table_info({table});")  # 获取表结构
    columns = cursor.fetchall()

    if columns:
        print(f"\nTable: {table}")
        for col in columns:
            print(f"Column: {col[1]}, Type: {col[2]}")

        # 检查表是否为空
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        count = cursor.fetchone()[0]
        if count == 0:
            print(f"Table {table} is empty.")
        else:
            print(f"Table {table} contains {count} records.")

            # 打印表中的前30条记录
            cursor.execute(f"SELECT * FROM {table} LIMIT 30;")
            rows = cursor.fetchall()
            print("\nFirst 30 records in the table:")
            for row in rows:
                print(row)
    else:
        print(f"\nTable {table} 不存在！")

conn.close()


# import sqlite3
#
# db_path = r"D:/项目与竞赛/深度学习与人工智能/agent_all/data/db.db"  # 确保路径正确
# conn = sqlite3.connect(db_path)
# cursor = conn.cursor()
#
# # 删除 assignments_submissions 表中的所有数据
# cursor.execute("DELETE FROM ai_resources;")
# print("All records have been deleted from the assignments_submissions table.")
#
# # 提交事务
# conn.commit()
#
# # 关闭连接
# conn.close()

# import sqlite3
# from datetime import datetime, timedelta
# import random
#
#
# def random_date(start, end):
#     """Generate a random datetime between `start` and `end`"""
#     return start + timedelta(
#         seconds=random.randint(0, int((end - start).total_seconds()))
#     )
#
#
# db_path = r"D:\项目与竞赛\agent_3\data\db.db"  # 确保路径正确
# conn = sqlite3.connect(db_path)
# cursor = conn.cursor()
#
# # 定义要插入的数据量
# num_records = 50
#
# # 随机生成数据并插入
# for i in range(1, num_records + 1):
#     assignment_id = random.randint(1, 100)  # 假设 assignment_id 在 1 到 100 之间
#     student_id = random.randint(1, 3)  # 假设 student_id 在 1 到 3 之间
#     submission_date = random_date(datetime(2023, 1, 1), datetime.now())
#     answers = f"Answer {i}"
#     grade = round(random.uniform(0, 100), 2)  # 成绩在 0 到 100 之间，保留两位小数
#     feedback = f"Feedback for answer {i}"
#     created_at = random_date(datetime(2023, 1, 1), datetime.now())
#     updated_at = random_date(created_at, datetime.now())  # 更新时间应该在创建时间之后
#
#     cursor.execute("""
#         INSERT INTO assignments_submissions
#         (id, assignment_id, student_id, submission_date, answers, grade, feedback, created_at, updated_at)
#         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
#     """, (i, assignment_id, student_id, submission_date, answers, grade, feedback, created_at, updated_at))
#
# # 提交事务
# conn.commit()
# print(f"{num_records} records have been inserted into the assignments_submissions table.")
#
# # 关闭连接
# conn.close()

# import sqlite3
#
# db_path = r"D:\项目与竞赛\agent_3\data\db.db"  # 确保路径正确
# conn = sqlite3.connect(db_path)
# cursor = conn.cursor()
#
# # 定义要插入的三条记录
# records_to_insert = [
#     {
#         'resource_name': '八下教案.txt',
#         'resource_type': 'txt',  # 资源类型
#         'file_path': r"D:\项目与竞赛\agent_3\AI\data\教案\八下教案.txt",  # 文件路径或URL
#         'user_id': 2,  # 用户ID
#         'created_at': '2025-03-21 17:40:00',  # 创建时间
#         'updated_at': '2025-03-21 17:40:00'   # 更新时间
#     },
#     {
#         'resource_name': '高二教案.txt',
#         'resource_type': 'txt',  # 资源类型
#         'file_path': r"D:\项目与竞赛\agent_3\AI\data\教案\高二教案.txt",  # 文件路径或URL
#         'user_id': 2,  # 用户ID
#         'created_at': '2025-03-21 17:45:00',  # 创建时间
#         'updated_at': '2025-03-21 17:45:00'   # 更新时间
#     },
#     {
#         'resource_name': '高二上学期教案.txt',
#         'resource_type': 'txt',  # 资源类型
#         'file_path': r"D:\项目与竞赛\agent_3\AI\data\教案\高二上学期教案.txt",  # 文件路径或URL
#         'user_id': 2,  # 用户ID
#         'created_at': '2025-03-21 17:50:00',  # 创建时间
#         'updated_at': '2025-03-21 17:50:00'   # 更新时间
#     }
# ]
#
# # 插入每条记录
# for record in records_to_insert:
#     cursor.execute("""
#         INSERT INTO resources (resource_name, resource_type, file_path, user_id, created_at, updated_at)
#         VALUES (?, ?, ?, ?, ?, ?);
#     """, (
#         record['resource_name'],
#         record['resource_type'],
#         record['file_path'],
#         record['user_id'],
#         record['created_at'],
#         record['updated_at']
#     ))
#
# # 提交更改
# conn.commit()
#
# print(f"{len(records_to_insert)} 条记录已成功添加到 resources 表中")
#
# # 关闭连接
# conn.close()
