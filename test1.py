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