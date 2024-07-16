# 安裝 psycopg2-binary
# pip install psycopg2-binary

import json
import time
import psycopg2
from datetime import date

class DBConnect:
    def __init__(self, printlog=False, host=None, port=None, dbname=None, user=None, password=None):
        self.conn = None
        self.printlog = printlog
        self.host = host
        self.port = port
        self.dbname = dbname
        self.user = user
        self.password = password
        self.connect()

    def check_type(self, value):
        """檢查並轉換數據類型"""
        if isinstance(value, date):
            # 將日期轉換為字符串格式
            value = value.strftime('%Y-%m-%d')
        elif isinstance(value, str):
            # 確保字串是 UTF-8 編碼
            value = value.encode('utf-8').decode('utf-8')
        return value

    def check_connect(self):
        """檢查連接是否有效，無效則重連"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT 1")
                if self.printlog:
                    print("Connection SUCCESS")
        except (psycopg2.DatabaseError, psycopg2.OperationalError) as e:
            print(f"Connection error: {e}")
            self.close(commit=False)
            self.connect()

    def connect(self):
        """建立資料庫連接"""
        if self.conn is None or self.conn.closed != 0:
            try:
                conn_string = (
                    f"host={self.host} port={self.port} dbname={self.dbname} "
                    f"user={self.user} password={self.password}"
                )
                self.conn = psycopg2.connect(conn_string)
                if self.printlog:
                    print(f"Connected to {self.host}")
            except (psycopg2.DatabaseError, psycopg2.OperationalError) as e:
                print(f"Connection error: {e}")
                time.sleep(2)
                self.connect()

    def execute(self, sql, params=None):
        """執行 SQL 語句"""
        try:
            if self.printlog:
                print(f"Executing SQL: {sql}")
                if params:
                    print(f"Params: {params}")

            with self.conn.cursor() as cur:
                cur.execute(sql, params)
            self.commit()
        except psycopg2.DatabaseError as e:
            print(f"Execute error: {e}")

    def query(self, sql, params=None):
        """執行查詢並返回結果的 JSON 字串"""
        try:
            if self.printlog:
                print(f"Executing SQL: {sql}")
                if params:
                    print(f"Params: {params}")

            with self.conn.cursor() as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()
                columns = [desc[0] for desc in cur.description]

                results = []
                for row in rows:
                    row_dict = {col: self.check_type(value) for col, value in zip(columns, row)}
                    results.append(row_dict)

                return results
        except psycopg2.DatabaseError as e:
            print(f"Query error: {e}")
            return []

    def commit(self):
        """提交交易"""
        self.conn.commit()

    def close(self, commit=True):
        """關閉連接"""
        if self.conn is not None:
            if commit:
                self.commit()
            try:
                self.conn.close()
                if self.printlog:
                    print(f"Connection to {self.host} closed")
            except psycopg2.DatabaseError as e:
                print(f"Error closing connection: {e}")
            finally:
                self.conn = None
