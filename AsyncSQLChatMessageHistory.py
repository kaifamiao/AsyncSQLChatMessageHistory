import asyncio
import aiosqlite
from datetime import datetime

class AsyncSQLChatMessageHistory:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None


    async def connect(self):
        """建立数据库连接并创建表"""
        self.conn = await aiosqlite.connect(self.db_path)
        await self._create_table()

    async def _create_table(self):
        """创建用于存储消息的历史表"""
        query = """
        CREATE TABLE IF NOT EXISTS message_store (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            message TEXT NOT NULL,
            message_type  NOT NULL,
            message_info TEXT,
            user_id TEXT NOT NULL,
            user_token TEXT,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
        await self.conn.execute(query)
        await self.conn.commit()

    async def add_message(self, session_id, message, message_type,message_info=None, user_id=None, user_token=None):
        """添加一条新的消息到数据库"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        query = """
        INSERT INTO message_store (session_id, message, message_type, message_info, user_id, user_token, create_time)
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        await self.conn.execute(query, (session_id, message, message_type, message_info, user_id, user_token, current_time))
        await self.conn.commit()

    async def get_messages(self, session_id):
        """获取特定会话的所有消息"""
        query = """
        SELECT * FROM message_store WHERE session_id = ? ORDER BY create_time;
        """
        cursor = await self.conn.execute(query, (session_id,))
        rows = await cursor.fetchall()
        return rows

    async def delete_message(self, message_id):
        """根据消息ID删除消息"""
        query = """
        DELETE FROM message_store WHERE id = ?;
        """
        await self.conn.execute(query, (message_id,))
        await self.conn.commit()

    async def update_message(self, message_id, new_message, new_message_info=None):
        """根据消息ID更新消息内容和附加信息"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        query = """
        UPDATE message_store SET message = ?, message_info = ?, create_time = ? WHERE id = ?;
        """
        await self.conn.execute(query, (new_message, new_message_info, current_time, message_id))
        await self.conn.commit()

    async def close(self):
        """关闭数据库连接"""
        if self.conn:
            await self.conn.close()
