import aiosqlite
from langchain.schema import AIMessage, HumanMessage
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory


async def generate_store_content_from_db(session_id,db_path):
    store = {}

    # 异步连接到SQLite数据库
    async with aiosqlite.connect(db_path) as db:
        # 为每个chat_history创建一个InMemoryChatMessageHistory对象
        history = InMemoryChatMessageHistory()

        # 查询该chat_history的所有消息
        async with db.execute("SELECT message, message_type FROM message_store WHERE session_id = ? ORDER BY id",
                              (session_id,)) as cursor:
            messages = await cursor.fetchall()

        for message, message_type in messages:
            if message_type == 'human':
                history.add_message(HumanMessage(content=message))
            elif message_type == 'ai':
                history.add_message(AIMessage(content=message))

        # 将生成的历史记录添加到store中
        store[session_id] = history

    return store


# 使用异步函数的示例
import asyncio


# async def main():
#     db_path = 'chat_history.db'  # 替换为您的SQLite数据库文件路径
#     store = await generate_store_content_from_db(db_path)
#     print(store)
#     # # 打印结果
#     # for key, value in store.items():
#     #     print(f"store['{key}'] = {value}")
#
#
# # 运行异步主函数
# if __name__ == "__main__":
#     asyncio.run(main())
