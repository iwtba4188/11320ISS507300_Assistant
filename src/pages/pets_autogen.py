import asyncio
import os
from collections import deque

import streamlit as st
from autogen import (
    ConversableAgent,
    LLMConfig,
    UserProxyAgent,
)
from autogen.io.run_response import AsyncRunResponseProtocol

from utils.bots import (
    a_chat,
    display_chat_history,
)
from utils.ctx_mgr import CtxMgr
from utils.function_call.pets import get_awaiting_adoption_pet_info
from utils.helpers import info_badge, read_file_content, str_stream, success_badge
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


def autogen_init(ctx_history: CtxMgr):
    llm_config_gemini = LLMConfig(
        api_type="google",
        model="gemini-2.5-flash-preview-04-17",  # The specific model
        api_key=GEMINI_API_KEY,  # Authentication
        stream=True,
    )

    user_proxy = UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        llm_config=llm_config_gemini,
        code_execution_config={
            "use_docker": False,
        },
        function_map={"get_awaiting_adoption_pet_info": get_awaiting_adoption_pet_info},
    )

    pets_expert = ConversableAgent(
        name="pets_expert",
        system_message=read_file_content("./src/static/expert_system_prompt.txt")
        + "盡可能使用 functions 中的函數來取得資料",
        human_input_mode="NEVER",
        llm_config=llm_config_gemini,
        functions=[
            get_awaiting_adoption_pet_info,
        ],
        code_execution_config={
            "use_docker": False,
        },
    )

    chat_result = user_proxy.initiate_chat(
        pets_expert,
        message=f"Introduce yourself, including who your role and what you can do. Language: {i18n.lang}.",
        max_turns=1,
        summary_method="last_msg",
    )
    st.chat_message("assistant").write_stream(str_stream(chat_result.summary))
    ctx_history.add_context({"role": "assistant", "content": chat_result.summary})

    st.session_state.user_proxy, st.session_state.pets_expert = user_proxy, pets_expert


async def autogen_response(prompt: str):
    user_proxy: UserProxyAgent = st.session_state.user_proxy
    pets_expert: ConversableAgent = st.session_state.pets_expert

    result: AsyncRunResponseProtocol = await user_proxy.a_run(
        pets_expert, clear_history=False, message=prompt, tools=user_proxy.tools
    )

    async for chunk in result.events:
        print(chunk)
        if chunk.type == "text" and chunk.content.recipient == "user_proxy":
            yield str_stream(chunk.content.content)
            return
        elif chunk.type == "execute_function":
            yield str_stream(info_badge(f"`{chunk.content.func_name}`"))
        elif chunk.type == "tool_response":
            yield str_stream(success_badge("success!"))


def chat_bot() -> None:
    """
    Render the chat interface and process user input in Streamlit.

    Creates a bordered container to display chat history and a chat input field.
    When the user submits a message, calls chat() inside the same container to
    render and stream the assistant's response.
    """
    chat_container = st.container(border=True)

    with chat_container:
        if ctx_history.size() == 0:
            autogen_init(ctx_history)
        else:
            display_chat_history(ctx_history)

    print("##### Rerun")
    if prompt := st.chat_input(placeholder=input_field_placeholder, key="chat_bot"):
        # if "chat_loop" in st.session_state:
        #     st.session_state.future.set_result(prompt)
        #     st.session_state.future = None
        #     print(f"User input set to future: {prompt}")
        #     return

        with chat_container:
            asyncio.run(a_chat(ctx_history, prompt=prompt, res_func=autogen_response))


if __name__ == "__main__":
    page_init()
    chat_bot()
