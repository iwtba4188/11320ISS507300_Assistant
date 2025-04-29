from typing import Generator

import streamlit as st


def display_chat_history(
    user_image: str = "https://www.w3schools.com/howto/img_avatar.png",
) -> None:
    """
    Render past user and assistant messages from
    st.session_state.history using Streamlit chat messages.
    """
    if "history" not in st.session_state:
        st.session_state.history = []
    histories = st.session_state.get("history", [])
    for history in histories:
        avatar = user_image if history["role"] == "user" else None
        st.chat_message(history["role"], avatar=avatar).markdown((history["content"]))


def chat(prompt: str, stream: Generator):
    """
    Post the user's prompt, invoke response streaming, and append messages to
    session state history.

    Arguments:
        prompt (str): Text entered by the user
    """
    user_image = "https://www.w3schools.com/howto/img_avatar.png"

    st.chat_message("user", avatar=user_image).write(prompt)
    st.session_state.history.append({"role": "user", "content": prompt})

    full_response = st.chat_message("assistant").write_stream(stream)

    if isinstance(full_response, str):
        full_response = [full_response]

    for response in full_response:
        st.session_state.history.append({"role": "assistant", "content": response})
