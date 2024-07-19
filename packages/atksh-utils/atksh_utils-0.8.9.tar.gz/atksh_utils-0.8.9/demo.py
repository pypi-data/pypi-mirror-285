import os

import streamlit as st

from atksh_utils.openai import OpenAI

st.title("My Chatbot")

key = os.getenv("OPENAI_API_KEY")
ai = OpenAI(key, "gpt-4o")
ai.set_bash_function()
ai.set_utility_functions()
ai.set_browser_functions()
ai.set_python_functions()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages[6:]:
    role = message["role"] if isinstance(message, dict) else message.role
    if role in ["user", "assistant"]:
        with st.chat_message(role):
            st.markdown(message["content"] if isinstance(message, dict) else message.content)

if prompt := st.chat_input("What is up?"):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        messages = st.session_state.messages
        if len(messages) == 0:
            messages, message = ai(prompt, is_question=True)
        else:
            messages.append({"role": "user", "content": prompt})
            ai.try_call(prompt, messages=messages)
            message = messages[-1].content
        response = st.markdown(message)
        st.session_state.messages = messages
