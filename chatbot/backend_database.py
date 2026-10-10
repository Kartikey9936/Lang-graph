from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage,HumanMessage
from langchain_groq import ChatGroq
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import sqlite3




load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):
    messages = state['messages']
    response = llm.invoke(messages)
    return {"messages": [response]}


conn = sqlite3.connect(database='chatbot.db',check_same_thread= False)
# we have made connection object
#here we have made false , bacause sqlite only supports single thread operations

# Checkpointer
# checkpointer = InMemorySaver()
checkpointer = SqliteSaver(conn=conn)

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

# checkpointer.list(None) #it give checkpoint of all thread so we have None or we can find for specific thread
# print(checkpointer.list(None)) # it give generator obj so we can run a loop
# 
# we can find unique thread in our detabase 
def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])

    return list(all_threads)









#here we have made stream object
#it is a generator object which will yield the response from the model in a streaming manner.
# stream =chatbot.stream(
#     {"messages": [HumanMessage(content="Hello, how are you?")]},
#     config={"configurable": {"thread_id": "thread-1"}},
#     stream_mode = 'messages'
# )

# for message_chunk,metadata in chatbot.stream(
#     {"messages": [HumanMessage(content="Hello, how are you?")]},
#     config={"configurable": {"thread_id": "thread-1"}},
#     stream_mode = 'messages'
# ):
#     if message_chunk.content:
#         print(message_chunk.content, end='', flush=True)