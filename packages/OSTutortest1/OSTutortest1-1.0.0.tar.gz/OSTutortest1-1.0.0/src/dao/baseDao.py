import sqlite3
from dataclasses import dataclass
from typing import Tuple
from contextlib import contextmanager
import os

@dataclass
class BaseDao:
    path = os.path.dirname(os.path.abspath(__file__))
    db:   str = os.path.join(path,'../assets/db/ostutor.db')
    sql:  str = os.path.join(path,'../assets/sql/ostutor.sql')
    conn: sqlite3.Connection = None
    cur:  sqlite3.Cursor     = None

    def createDatabase(self):
        """
        创建数据库
        """
        with self.connect() as (conn, cur):
            with open(self.sql,'r') as file:
                sql = file.read()

            cur.executescript(sql)

            self.commit()

    @contextmanager
    def connect(self):
        """
        连接数据库
        """
        try:
            if os.path.exists(self.db):
                self.conn = sqlite3.connect(self.db)
                self.cur = self.conn.cursor()
                yield self.conn, self.cur
            else:
                print("File does not exist")
                raise FileNotFoundError(f"Database file '{self.db}' does not exist")
        finally:
            self.close()

    def getConnection(self) -> Tuple[sqlite3.Connection, sqlite3.Cursor]: 
        """
        获取连接
        """ 
        if self.conn == None: 
            self.conn = sqlite3.connect(self.db)
            self.cur = self.conn.cursor()

        return self.conn, self.cur

    def commit(self): 
        """
        提交事务
        """
        self.conn.commit()


    def close(self): 
        """
        关闭链接
        """
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

    def commitandclose(self):
        """
        提交并关闭链接
        """
        self.conn.commit()
        self.cur.close()
        self.conn.close()

    def add_table(self):
        """
        在已经创建好的表里增加新表，供开发使用
        """
        create_synonyms_table = '''
        DROP TABLE IF EXISTS synonyms;

        CREATE TABLE synonyms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            synonym TEXT NOT NULL
        );
        '''

        try:
            # 连接到 SQLite 数据库
            conn = sqlite3.connect(self.db)
            cursor = conn.cursor()
            cursor.executescript(create_synonyms_table)
            conn.commit()
            print("运行成功")
        except sqlite3.Error as e:
            print(f"数据库错误: {e}")
        finally:
            if conn:
                conn.close()
    