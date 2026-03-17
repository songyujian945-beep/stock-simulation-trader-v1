#!/usr/bin/env python3
"""
股票模拟交易系统 - 数据库管理
"""
import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class DatabaseManager:
    """数据库管理器"""

    def __init__(self, db_path: str = "data/stock_trader.db"):
        """初始化数据库"""
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_tables()

    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_tables(self):
        """初始化数据表"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # 股票池表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS stocks_pool (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL,
            name TEXT NOT NULL,
            industry TEXT,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active'
        )
        """)

        # 持仓表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL,
            name TEXT NOT NULL,
            buy_price REAL NOT NULL,
            current_price REAL,
            shares INTEGER NOT NULL,
            buy_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            profit REAL DEFAULT 0,
            profit_rate REAL DEFAULT 0,
            status TEXT DEFAULT 'holding'
        )
        """)

        # 交易记录表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            price REAL NOT NULL,
            shares INTEGER NOT NULL,
            amount REAL NOT NULL,
            fee REAL DEFAULT 0,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reason TEXT
        )
        """)

        # 账户表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS account (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            initial_capital REAL DEFAULT 50000,
            available_cash REAL DEFAULT 50000,
            market_value REAL DEFAULT 0,
            total_asset REAL DEFAULT 50000,
            total_profit REAL DEFAULT 0,
            total_profit_rate REAL DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # 初始化账户
        cursor.execute("SELECT COUNT(*) FROM account")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
            INSERT INTO account (initial_capital, available_cash, market_value, total_asset)
            VALUES (50000, 50000, 0, 50000)
            """)

        conn.commit()
        conn.close()

    # 账户操作
    def get_account(self) -> Dict:
        """获取账户信息"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM account ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return {
            'initial_capital': 50000,
            'available_cash': 50000,
            'market_value': 0,
            'total_asset': 50000,
            'total_profit': 0,
            'total_profit_rate': 0
        }

    def update_account(self, **kwargs):
        """更新账户信息"""
        conn = self.get_connection()
        cursor = conn.cursor()

        fields = []
        values = []
        for key, value in kwargs.items():
            fields.append(f"{key} = ?")
            values.append(value)

        values.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        sql = f"UPDATE account SET {', '.join(fields)}, updated_at = ? WHERE id = 1"

        cursor.execute(sql, values)
        conn.commit()
        conn.close()

    def update_account_v2(self, **kwargs):
        """更新账户信息（v2版，只更新可用现金）"""
        conn = self.get_connection()
        cursor = conn.cursor()

        fields = []
        values = []
        for key, value in kwargs.items():
            fields.append(f"{key} = ?")
            values.append(value)

        values.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        sql = f"UPDATE account SET {', '.join(fields)}, updated_at = ? WHERE id = 1"

        cursor.execute(sql, values)
        conn.commit()
        conn.close()

    # 持仓操作
    def get_positions(self) -> List[Dict]:
        """获取所有持仓"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM positions WHERE status = 'holding' ORDER BY buy_time DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def add_position(self, code: str, name: str, buy_price: float, shares: int):
        """添加持仓"""
        conn = self.get_connection()
        cursor = conn.cursor()
        # 使用本地时间，不是UTC
        buy_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
        INSERT INTO positions (code, name, buy_price, shares, buy_time)
        VALUES (?, ?, ?, ?, ?)
        """, (code, name, buy_price, shares, buy_time))
        conn.commit()
        conn.close()

    def update_position(self, code: str, **kwargs):
        """更新持仓信息"""
        conn = self.get_connection()
        cursor = conn.cursor()

        fields = []
        values = []
        for key, value in kwargs.items():
            fields.append(f"{key} = ?")
            values.append(value)

        values.append(code)
        sql = f"UPDATE positions SET {', '.join(fields)} WHERE code = ? AND status = 'holding'"

        cursor.execute(sql, values)
        conn.commit()
        conn.close()

    def remove_position(self, code: str):
        """卖出持仓"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE positions SET status = 'sold' WHERE code = ? AND status = 'holding'", (code,))
        conn.commit()
        conn.close()

    # 交易记录
    def add_transaction(self, code: str, name: str, trans_type: str,
                       price: float, shares: int, amount: float,
                       fee: float = 0, reason: str = ""):
        """添加交易记录"""
        conn = self.get_connection()
        cursor = conn.cursor()
        # 使用本地时间
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
        INSERT INTO transactions (code, name, type, price, shares, amount, fee, reason, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (code, name, trans_type, price, shares, amount, fee, reason, timestamp))
        conn.commit()
        conn.close()

    def get_transactions(self, limit: int = 50) -> List[Dict]:
        """获取交易记录"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM transactions
        ORDER BY timestamp DESC
        LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_all_transaction_fees(self) -> float:
        """获取所有交易手续费总和"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(fee) FROM transactions WHERE type = 'buy'")
        total_fees = cursor.fetchone()[0]
        conn.close()
        return total_fees if total_fees else 0.0

    def get_sell_fees(self) -> float:
        """获取所有卖出手续费总和"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(fee) FROM transactions WHERE type = 'sell'")
        total_fees = cursor.fetchone()[0]
        conn.close()
        return total_fees if total_fees else 0.0

    # 股票池
    def add_to_pool(self, code: str, name: str, industry: str = ""):
        """添加股票到股票池"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT OR IGNORE INTO stocks_pool (code, name, industry)
        VALUES (?, ?, ?)
        """, (code, name, industry))
        conn.commit()
        conn.close()

    def get_active_stocks(self) -> List[Dict]:
        """获取活跃股票池"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM stocks_pool WHERE status = 'active'")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def update_pool_status(self, code: str, status: str):
        """更新股票池状态"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE stocks_pool SET status = ? WHERE code = ?", (status, code))
        conn.commit()
        conn.close()

if __name__ == "__main__":
    db = DatabaseManager()
    print("数据库初始化完成")
    print("账户信息:", db.get_account())
