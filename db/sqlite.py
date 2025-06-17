import sqlite3
from typing import List, Dict, Any


class SqliteUtils:
    def __init__(self):
        pass

    def connect_db(self, db_path: str) -> sqlite3.Connection:
        """连接到指定的sqlite数据库文件，返回连接对象。"""
        try:
            conn = sqlite3.connect(db_path)
            return conn
        except sqlite3.Error as e:
            raise RuntimeError(f"无法连接到数据库: {e}")

    def get_table_names(self, db_path: str) -> List[str]:
        """获取数据库中所有表名。"""
        conn = self.connect_db(db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            return tables
        finally:
            conn.close()

    def read_table(self, db_path: str, table_name: str) -> List[Dict[str, Any]]:
        """读取指定表的所有数据，返回为list of dict。"""
        conn = self.connect_db(db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name}")
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            result = [dict(zip(columns, row)) for row in rows]
            return result
        finally:
            conn.close()
