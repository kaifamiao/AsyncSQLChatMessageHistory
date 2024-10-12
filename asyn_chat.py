import asyncio
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, FileResponse
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_community.chat_models import ChatOllama
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from AsyncSQLChatMessageHistory import AsyncSQLChatMessageHistory
from create_store import generate_store_content_from_db
session_id = 'abc5'
store={}
print(f"Store initialized successfully {store}")
async def update_store():
    global store
    db_path = './chat_history.db'  # 替换为您的SQLite数据库文件路径
    store = await generate_store_content_from_db(session_id, db_path)

# 初始化函数
async def initialize_store():
    await update_store()
    print("Store initialized successfully initialize_store(): ", store)

# 在程序启动时运行这个函数来初始化 store
# initialize_store()
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] =InMemoryChatMessageHistory()
    return store[session_id]

async def get_messages(session_id):
    chat_history = AsyncSQLChatMessageHistory('chat_history.db')
    await chat_history.connect()
    messages = await chat_history.get_messages(session_id)
    await chat_history.close()
    return messages


async def add_message_to_history(session_id, message, message_type):
    chat_history = AsyncSQLChatMessageHistory('chat_history.db')
    await chat_history.connect()
    await chat_history.add_message(session_id, message, message_type, 'First message', 'kfm', '123456')


kfm_llm = ChatOllama(
    model="qwen2",
    temperature=0.1,
    top_p=0.9,
    max_length=4098,
    streaming=True,
)

def get_with_msg_history(llm):
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant."),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    chain = prompt | llm
    with_message_history = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="messages",
    )
    return with_message_history

async def generate_chat_responses(message):
    config = {"configurable": {"session_id": session_id}}
    await add_message_to_history(session_id, message, 'human')
    msg=''
    async for chunk in get_with_msg_history(kfm_llm).astream(
            {"messages": [HumanMessage(content=message)]},
            config=config
    ):
        content = chunk.content
        msg+=content
        print(content)
        yield f"data: {content}\n\n"
    await add_message_to_history(session_id, msg, 'ai')
app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/chat_stream/{message}")
async def chat_stream(message: str):
    print("============================================================================================")
    print(f"store: {store}")
    print(f"/chat_stream/{message}")
    return StreamingResponse(generate_chat_responses(message=message), media_type="text/event-stream")


@app.get("/get_session_history/")
async def get_history():
    print("get_session_history")
    messages = await get_messages(session_id)
    return messages

@app.get("/get_store/")
async def get_store():
    print("get_session_history")
    print(store)
    return store
@app.get("/")
async def root():
    await initialize_store()
    return FileResponse("static/index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)