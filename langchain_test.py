from langchain_community.chat_models import ChatOllama
from langchain_core.chat_history import (
    BaseChatMessageHistory,
    InMemoryChatMessageHistory,
)
from langchain_core.messages import HumanMessage
from langchain_core.runnables.history import RunnableWithMessageHistory

store = {}

model = ChatOllama(
    model="qwen2",
    temperature=0.1,
    top_p=0.9,
    max_length=4098,
    streaming=True,  # 启用流式生成,
)
store={}
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

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

# Add a message to the history
config = {"configurable": {"session_id": "abc5"}}

response_stream1 = with_message_history.invoke(
    [HumanMessage(content="我叫林睿")],
    config=config,
)
response_stream2 = with_message_history.invoke(
    [HumanMessage(content="你叫什么名字")],
    config=config,
)
response_stream3 = with_message_history.invoke(
        [HumanMessage(content="你可以做什么")],

    config=config,
)

response_stream4 = with_message_history.stream(

        [HumanMessage(content="我叫什么名字")],

    config=config,
)
for chunk in response_stream4:
    print(chunk.content, end="", flush=True)
