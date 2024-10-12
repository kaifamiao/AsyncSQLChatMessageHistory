#

langchain里为了实现历史对话，有一个SQLChatMessageHistory，可用于历史记录的存储，非常好用
但是它langchain做了诸多限制，特别是在用到异步上面非常不方便。
我把SQLChatMessageHistory重新写了一个AsyncSQLChatMessageHistory，异步版本的SQLChatMessageHistory，可以更方便的使用异步操作
```python
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

```
### 使用方法：
```python
import asyncio
import json

from langchain_core.messages import AIMessageChunk

from AsyncSQLChatMessageHistory import AsyncSQLChatMessageHistory

async def main():
    chat_history = AsyncSQLChatMessageHistory('chat_history.db')
    await chat_history.connect()

    # 示例 AIMessageChunk 实例
    ai_message_chunk = AIMessageChunk(content="记住了。")

    # 将 AIMessageChunk 转换为字典
    ai_message_dict = {
        "type": "ai",
        "data": {
            "content": ai_message_chunk.content,
            "additional_kwargs": {},
            "response_metadata": {},
            "type": "ai",
            "name": None,
            "id": None,
            "example": False,
            "tool_calls": [],
            "invalid_tool_calls": [],
            "usage_metadata": None
        }
    }

    # 将字典转换为 JSON
    ai_message_json = json.dumps(ai_message_dict, ensure_ascii=False)
    print(ai_message_json)

    # 示例 HumanMessageChunk 字典
    human_message_dict = {
        "type": "human",
        "data": {
            "content": "我叫林睿",
            "additional_kwargs": {},
            "response_metadata": {},
            "type": "human",
            "name": None,
            "id": None,
            "example": False
        }
    }

    # 将字典转换为 JSON
    human_message_json = json.dumps(human_message_dict, ensure_ascii=False)
    print(human_message_json)

    # 添加消息

    await chat_history.add_message('abc5', human_message_json,'human', 'First message', 'kfm', '123456')
    #
    await chat_history.add_message('abc5', ai_message_json, 'ai','Second message', 'kfm', '123456')

    # 获取会话的消息
    messages = await chat_history.get_messages('session23')
    for msg in messages:
        print(msg)

    # 关闭连接
    await chat_history.close()

# 运行异步函数
if __name__ == '__main__':
    asyncio.run(main())
```
### 在chain中使用
```python
import asyncio
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_community.chat_models import ChatOllama
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from AsyncSQLChatMessageHistory import AsyncSQLChatMessageHistory
from create_store import generate_store_content_from_db
store={}
async def update_store():
    global store
    db_path = './chat_history.db'  # 替换为您的SQLite数据库文件路径
    store = await generate_store_content_from_db('abc5', db_path)

# 初始化函数
def initialize_store():
    asyncio.run(update_store())
    print("Store initialized successfully")
# 在程序启动时运行这个函数来初始化 store
initialize_store()
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] =InMemoryChatMessageHistory()
    return store[session_id]

# async def get_messages(session_id):
#     chat_history = AsyncSQLChatMessageHistory('chat_history.db')
#     await chat_history.connect()
#     messages = await chat_history.get_messages(session_id)
#     await chat_history.close()
#     return messages


async def add_message_to_history(session_id, message, message_type):
    chat_history = AsyncSQLChatMessageHistory('chat_history.db')
    await chat_history.connect()
    await chat_history.add_message(session_id, message, message_type, 'First message', 'kfm', '123456')

async def main():
    model = ChatOllama(
        model="qwen2",
        temperature=0.1,
        top_p=0.9,
        max_length=4098,
        streaming=True,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful assistant. Answer all questions to the best of your ability.",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    chain = prompt | model

    with_message_history = RunnableWithMessageHistory(chain, get_session_history)

    config = {"configurable": {"session_id": "abc5"}}
    print(f"stroe1[{len(store)}]", store)
    #
    # response_stream1 = await with_message_history.ainvoke(
    #     [HumanMessage(content="我叫林睿")],
    #     config=config,
    # )
    # print(response_stream1.content)
    # await add_message_to_history('abc5', '我叫林睿', 'human')
    # await add_message_to_history('abc5', response_stream1.content, 'ai')
    # print(f"stroe2[{len(store)}]", store)
    #
    # response_stream2 = await with_message_history.ainvoke(
    #     [HumanMessage(content="你叫什么名字")],
    #     config=config,
    # )
    # await add_message_to_history('abc5', '你叫什么名字', 'human')
    # await add_message_to_history('abc5', response_stream2.content, 'ai')
    # print(f"stroe3[{len(store)}]", store)
    #
    # response_stream3 =await with_message_history.ainvoke(
    #     [HumanMessage(content="你可以做什么")],
    #     config=config,
    # )
    # await add_message_to_history('abc5', '你可以做什么', 'human')
    # await add_message_to_history('abc5', response_stream3.content, 'ai')
    # print(f"stroe4[{len(store)}]", store)

    response_stream4 = with_message_history.astream(
        [HumanMessage(content="我叫什么名字")],
        config=config,
    )
    await add_message_to_history('abc5', '我叫什么名字', 'human')
    print(f"stroe5[{len(store)}]", store)
    msg=""
    async for chunk in response_stream4:
        msg+=chunk.content
        print(chunk.content, end="", flush=True)

    await add_message_to_history('abc5', msg, 'ai')
if __name__ == "__main__":
    asyncio.run(main())

```