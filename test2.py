import asyncio

from AsyncSQLChatMessageHistory import AsyncSQLChatMessageHistory


# 使用示例
async def main():
    chat_history = AsyncSQLChatMessageHistory('chat_history.db')
    await chat_history.connect()

    # 添加消息
    await chat_history.add_message('session1', 'Hello, world!', 'First message', 'user1', ' token1')
    await chat_history.add_message('session2', 'Hi there!', 'Second message', 'user2', 'token2')

    # 获取会话的消息
    messages = await chat_history.get_messages('session1')
    for msg in messages:
        print(msg)

    # 更新消息
    message_id_to_update = messages[0][0]  # 假设我们要更新第一条消息
    await chat_history.update_message(message_id_to_update, 'Updated message', 'Updated info')

    # 删除消息
    message_id_to_delete = messages[1][0]  # 假设我们要删除第二条消息
    await chat_history.delete_message(message_id_to_delete)

    # 再次获取会话的消息
    updated_messages = await chat_history.get_messages('session1')
    for msg in updated_messages:
        print(msg)

    # 关闭连接
    await chat_history.close()

# 运行异步函数
if __name__ == '__main__':
    asyncio.run(main())