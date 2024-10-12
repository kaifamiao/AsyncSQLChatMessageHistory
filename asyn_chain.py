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
