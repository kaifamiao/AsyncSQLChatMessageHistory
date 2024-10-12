import sqlite3
from langchain.schema import AIMessage, HumanMessage
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory


async def generate_store_content_from_db(db_path):
    store = {}

    # 连接到SQLite数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 查询所有唯一的chat_history值
    cursor.execute("SELECT DISTINCT session_id FROM message_store")
    chat_histories = cursor.fetchall()

    for (chat_history,) in chat_histories:
        # 为每个chat_history创建一个InMemoryChatMessageHistory对象
        history = InMemoryChatMessageHistory()

        # 查询该chat_history的所有消息
        cursor.execute("SELECT message, message_type FROM message_store WHERE session_id = ? ORDER BY id",
                       (chat_history,))
        messages = cursor.fetchall()

        for message, message_type in messages:
            if message_type == 'human':
                history.add_message(HumanMessage(content=message))
            elif message_type == 'ai':
                history.add_message(AIMessage(content=message))

        # 将生成的历史记录添加到store中
        store[chat_history] = history

    # 关闭数据库连接
    conn.close()

    return store


# 使用函数
db_path = './chat_history.db'  # 替换为您的SQLite数据库文件路径
store = generate_store_content_from_db(db_path)

# print(store)
# # 打印结果
# for key, value in store.items():
#     print(f"store['{key}'] = {value}")
