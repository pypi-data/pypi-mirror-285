#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File : sql_session.py
@Create  : 2024-05-10 13:36
@Desc   : 封装pymysql执行sql
"""
import pymysql

class MySQLSession:
    def __init__(self, host: str, port: int, user: str, password: str, db: str):
        try:
            self.connection = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=db
            )
            self.connected = True
        except Exception as e:
            self.connected = False
            self.error = f"连接数据库失败: {e}"

    def execute_sql(self, sql: str):
        """
        执行MySQL查询

        参数:
        sql (str): 要执行的SQL查询语句

        返回: dict
        status: bool
        data: list
        """
        if not self.connected:
            return {
                "status": False,
                "data": self.error
            }
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql)
                if sql.strip().lower().startswith(('select', 'show', 'describe', 'desc')):
                    data = list(cursor.fetchall())
                    return {
                        "status": True,
                        "data": data
                    }
                else:
                    self.connection.commit()
                    return {
                        "status": True,
                        "data": "操作成功"
                    }
        except Exception as e:
            return {
                "status": False,
                "data": f"执行sql报错: {e}"
            }

    def close(self):
        if hasattr(self, 'connection') and self.connection:
            self.connection.close()

# 使用示例
if __name__ == "__main__":
    mysql_info = {
        'host': '192.168.4.55',
        'port': 3306,
        'user': 'root',
        'password': 'CuJia@567',
        'db': 'k8s'
    }
    session = MySQLSession(**mysql_info)

    if session.connected:
        # 执行查询
        result = session.execute_sql('SELECT * FROM rds_detail')
        print(result)

        # 执行插入
        insert_sql = "INSERT INTO rds_detail (column1, column2) VALUES ('value1', 'value2')"
        result = session.execute_sql(insert_sql)
        print(result)

        # 关闭会话
        session.close()
    else:
        print("数据库连接失败:", session.error)
