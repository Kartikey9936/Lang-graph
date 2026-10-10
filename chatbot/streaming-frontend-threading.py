import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage,AIMessage
import uuid
#by using this we can generate unique thread id for each thread and we can use this
#id to store the state of the graph for that particular thread in the checkpointer.

# **************************************** utility functions *************************
def generate_thread_id():#it will generate random unique thread id for each thread and we can use this
    thread_id = uuid.uuid4()
    return thread_id

# def reset_chat():
#     thread_id = generate_thread_id() 
#     add_thread(st.session_state['thread_id']) #add the new thread_id to the chat_threads list
#     st.session_state['thread_id'] = thread_id
#     st.session_state['message_history'] = [] #empty the message history for the new thread

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    st.session_state['message_history'] = []
    add_thread(thread_id)


def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    # Check if messages key exists in state values, return empty list if not
    return state.values.get('messages', [])

# **************************************** Session Setup ******************************
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

#we have to store the thread_id in the session state because we want to keep track of the thread_id for each thread and we can use this
if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = [] #chat_threads will store the thread_id and the message history for each thread.

if 'chat_names' not in st.session_state:
    st.session_state['chat_names'] = {}

add_thread(st.session_state['thread_id']) #add the current thread_id to the chat_threads list if it is not already present.




# **************************************** Sidebar UI *********************************
st.sidebar.title("LangGraph Chatbot")

if st.sidebar.button("New Chat"): #if user clicks on new chat button then we will reset the chat and generate new thread id for the new chat.
    reset_chat()

st.sidebar.header("My Chat History")

for thread_id in st.session_state['chat_threads'][::-1]:
    # st.sidebar.text(thread_id)
    # if st.sidebar.button(str(thread_id)):
    chat_name = st.session_state['chat_names'].get(
        thread_id, "Current Chat"
    )

    if st.sidebar.button(chat_name, key=str(thread_id)):
       st.session_state['thread_id'] = thread_id #store the thread_id into session
       messages = load_conversation(thread_id) #with current thread_id 

       temp_messages = []
       for msg in messages:
           if isinstance(msg,HumanMessage):
               role = 'user'
           else:
               role = 'assistant'
           temp_messages.append({'role':role,'content':msg.content})

       st.session_state['message_history'] = temp_messages

           


# **************************************** Main UI ************************************

# loading the conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input('Type here')

if user_input:
    thread_id = st.session_state['thread_id']

    if thread_id not in st.session_state['chat_names']:
       st.session_state['chat_names'][thread_id] = user_input[:30]

    # first add the message to message_history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

     # first add the message to message_history
    with st.chat_message("assistant"):
        def ai_only_stream():
            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages"
            ):
                if isinstance(message_chunk, AIMessage):
                    # yield only assistant tokens
                    yield message_chunk.content

        ai_message = st.write_stream(ai_only_stream())

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})


    