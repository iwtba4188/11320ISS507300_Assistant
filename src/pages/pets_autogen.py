import os
from collections import deque
from collections.abc import Generator

import streamlit as st
from autogen import (
    ConversableAgent,
    GroupChat,
    GroupChatManager,
    LLMConfig,
    UserProxyAgent,
)
from httpx import stream

from utils.bots import (
    chat,
    display_chat_history,
)
from utils.ctx_mgr import CtxMgr
from utils.function_call.pets import get_awaiting_adoption_pet_info
from utils.helpers import read_file_content
from utils.i18n import i18n

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", None)

input_field_placeholder = i18n("pets.chat.input_placeholder")
user_name = "Shihtl"
ctx_history = CtxMgr("pets_autogen_history", [])
ctx_content = CtxMgr("pets_autogen", deque(maxlen=20))


def page_init() -> None:
    """
    Set the Streamlit page title using the localized message and configured user name.
    """
    st.title(i18n("pets.chat.doc_title").format(user_name=user_name))
    st.markdown(
        """<style>
    div.stSpinner > div {
        padding-left: 55px;
    }
</style>""",
        unsafe_allow_html=True,
    )


def autogen_init(ctx_history: CtxMgr) -> tuple[UserProxyAgent, GroupChatManager]:
    def is_termination_msg(x):
        return x.get("content", "").rstrip().endswith("TERMINATE")

    llm_config_gemini = LLMConfig(
        api_type="google",
        model="gemini-2.0-flash-lite",  # The specific model
        api_key=GEMINI_API_KEY,  # Authentication
        stream=True,
    )

    user_proxy = UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",  # input() doesn't work, so needs to be "NEVER" here
        max_consecutive_auto_reply=10,
        is_termination_msg=is_termination_msg,
        code_execution_config=False,
        llm_config=llm_config_gemini,
        system_message="""""",
    )

    pets_expert = ConversableAgent(
        name="pets_expert",
        system_message=read_file_content("./src/static/expert_system_prompt.txt"),
        human_input_mode="NEVER",
        max_consecutive_auto_reply=2,
        llm_config=llm_config_gemini,
    )

    adoption_info_agent = ConversableAgent(
        name="adoption_info_agent",
        system_message="You can provide information about pets available for adoption.",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=2,
        llm_config=llm_config_gemini,
        functions=[
            get_awaiting_adoption_pet_info,
        ],
    )

    groupchat = GroupChat(
        agents=[
            user_proxy,
            pets_expert,
            adoption_info_agent,
        ],
        messages=[],
        speaker_selection_method="round_robin",
    )
    manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config_gemini)

    chat_result = manager.initiate_chat(
        manager,
        message="Introduce yourself, including who you are and what you can do.",
        max_turns=1,
    )
    full_response = st.chat_message("assistant").write_stream(chat_result.chat_history)
    ctx_history.add_context({"role": "assistant", "content": full_response})

    return user_proxy, manager


def autogen_response_stream(
    user_proxy: UserProxyAgent, manager: GroupChatManager
) -> Generator:
    result = user_proxy.run(manager, message=ctx_content.get_context()[0])
    for chunk in result:
        if isinstance(chunk, str):
            yield chunk
        elif isinstance(chunk, stream.Response):
            for line in chunk.iter_lines():
                if line:
                    yield line.decode("utf-8")
        elif isinstance(chunk, GroupChatManager):
            for message in chunk.messages:
                if message.role == "assistant":
                    yield message.content
        else:
            yield chunk.content


def chat_bot() -> None:
    """
    Render the chat interface and process user input in Streamlit.

    Creates a bordered container to display chat history and a chat input field.
    When the user submits a message, calls chat() inside the same container to
    render and stream the assistant's response.
    """
    if ctx_history.size() == 0:
        user_proxy, manager = autogen_init(ctx_history)

    chat_container = st.container(border=True)
    with chat_container:
        display_chat_history(ctx_history)

    if prompt := st.chat_input(placeholder=input_field_placeholder, key="chat_bot"):
        ctx_content.clear_context()
        ctx_content.add_context(prompt)
        with chat_container:
            chat(
                ctx_history,
                prompt=prompt,
                stream=autogen_response_stream(user_proxy, manager),
            )


if __name__ == "__main__":
    page_init()
    chat_bot()
