import os
import time
from collections import deque
from collections.abc import Generator

import streamlit as st
from google import genai
from google.genai import types

from utils.bots import (
    chat,
    display_chat_history,
)
from utils.bots.ctx_mgr import CtxMgr
from utils.function_call import (
    cawling_dcard_urls,
    content_wordcloud,
    crawling_dcard_article_content,
)
from utils.helpers import (
    error_badge,
    info_badge,
    read_file_content,
    st_spinner,
    str_stream,
    success_badge,
)
from utils.i18n import i18n

input_field_placeholder = i18n("pets.chat.input_placeholder")
user_name = "Shihtl"
ctx_history = CtxMgr("pets_gemini_history", [])
ctx_content = CtxMgr("pets_gemini", deque(maxlen=10))


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


def init_gemini_api_config() -> dict:
    """
    Build and return the initial Gemini API configuration with model, generation settings,
    and enabled tools.

    Returns:
        dict: {
            "model": (str) Gemini model name,
            "config": (GenerateContentConfig) generation parameters
        }
    """
    system_prompt = read_file_content("./src/static/system_prompt.txt")

    model = "gemini-2.5-flash-preview-04-17"
    # model = "gemini-2.0-flash"
    tools = [
        # get_awaiting_adoption_pet_info,
        cawling_dcard_urls,
        crawling_dcard_article_content,
        content_wordcloud,
    ]

    generate_content_config = types.GenerateContentConfig(
        temperature=0,
        # thinking_config=types.ThinkingConfig(
        #     include_thoughts=True,
        #     thinking_budget=250,
        # ),
        response_mime_type="text/plain",
        system_instruction=[
            types.Part.from_text(text=system_prompt),
        ],
        tools=tools,  # type: ignore
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )

    return {
        "model": model,
        "config": generate_content_config,
    }


def gemini_api_config() -> dict:
    """
    Retrieve or initialize the base Gemini API config, update it with current conversation
    contents, and return it.

    Returns:
        dict: Configuration including model, config parameters, and "contents" list
    """
    if "gemini_configs" not in st.session_state:
        gemini_configs: dict = init_gemini_api_config()
        st.session_state["gemini_configs"] = gemini_configs
    else:
        gemini_configs: dict = st.session_state["gemini_configs"]

    gemini_configs["contents"] = ctx_content.get_context()
    print(gemini_configs)
    return gemini_configs


def execute_func_call(func_call: types.FunctionCall) -> dict:
    """
    Execute the given function call, capture success or error, and return status
    and result.

    Arguments:
        func_call (types.FunctionCall): Function call object to execute

    Returns:
        dict: {
            "func_call": FunctionCall,
            "status": "success" or "error",
            "result": Function result or error message
        }
    """
    func_call_result = {
        "func_call": func_call,
        "status": "unknown",
        "result": "unknown",
        "display_result": False,
    }

    try:
        # if func_call.name == "get_awaiting_adoption_pet_info":
        #     func_call_result["status"] = "success"
        #     func_call_result["result"] = get_awaiting_adoption_pet_info()
        if func_call.name == "cawling_dcard_urls":
            func_call_result["status"] = "success"
            func_call_result["result"] = cawling_dcard_urls(**func_call.args)
        elif func_call.name == "crawling_dcard_article_content":
            func_call_result["status"] = "success"
            func_call_result["result"] = crawling_dcard_article_content(
                **func_call.args
            )
        elif func_call.name == "content_wordcloud":
            func_call_result["status"] = "success"
            func_call_result["result"] = content_wordcloud(**func_call.args)
            func_call_result["display_result"] = True
        # XXX: Extension point for other function calls
        else:
            raise ValueError(f"Unknown function call: {func_call.name}")
    except Exception as e:
        func_call_result["status"] = "error"
        func_call_result["result"] = str(e)

    return func_call_result


def add_func_call_result(func_call_result: dict) -> None:
    """
    Append model and user content entries for the executed function call and its
    response to session_state contents.

    Arguments:
        func_call_result (dict): Contains "func_call", "status", and "result".
    """
    function_response_part = types.Part.from_function_response(
        name=func_call_result["func_call"].name,
        response={"result": func_call_result["result"]},
    )
    ctx_content.add_context(
        types.Content(
            role="model",
            parts=[types.Part(function_call=func_call_result["func_call"])],
        )
    )
    ctx_content.add_context(types.Content(role="user", parts=[function_response_part]))


def func_call_result_badge_stream(func_call_result: dict) -> Generator:
    """
    Stream a badge indicating function call success or error, character by
    character.

    Arguments:
        func_call_result (dict): Contains "status" and "func_call" info.

    Yields:
        str: Characters forming the status badge message.
    """
    func_call_msg_i18n_key = f"pets.chat.badge.func_call_{func_call_result['status']}"
    func_call_msg = i18n(func_call_msg_i18n_key).format(
        func_name=func_call_result["func_call"].name
    )

    if func_call_result["status"] == "error":
        print(f"Error in function call: {func_call_result['result']}")
        yield from str_stream(error_badge(func_call_msg))
    else:
        yield from str_stream(success_badge(func_call_msg))

    if func_call_result["display_result"]:
        yield func_call_result["result"]


def gemini_function_calling(
    function_calls: list[types.FunctionCall],
) -> Generator:
    """
    Process a list of function calls: execute each, stream its badge, then prompt for next
    actions and continue with model response.

    Arguments:
        function_calls (list[types.FunctionCall]): FunctionCall objects to process.

    Yields:
        str: Characters of badge messages and subsequent model response.
    """
    for func_call in function_calls:
        spinner_func_call_text = i18n("pets.chat.spinner.func_call_text").format(
            func_call_name=func_call.name
        )

        with st.spinner(spinner_func_call_text, show_time=True):
            func_call_result = execute_func_call(func_call)
            add_func_call_result(func_call_result)
            time.sleep(1)  # Simulate some delay for the spinner

        yield from func_call_result_badge_stream(func_call_result)

    think_again_msg = i18n("pets.chat.badge.think_again")
    yield from str_stream(info_badge(think_again_msg))

    yield from gemini_response_stream()


def test_wordcloud():
    urls = cawling_dcard_urls()

    # collect first 10 urls' content
    contents = []
    for url in urls[:10]:
        contents.append(crawling_dcard_article_content(url[1])["content"])

    with st.chat_message("assistant"):
        # st.pyplot(content_wordcloud(contents))
        st.markdown(content_wordcloud(contents), unsafe_allow_html=True)


def gemini_response_stream() -> Generator:
    """
    Invoke the Gemini client to stream text chunks from the model, yield them, and
    record the full response and handle any function calls.

    Yields:
        str: Characters from the model's response and streams function call handling if needed.
    """
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    function_calls = []
    this_response = ""

    gemini_response_spinner = st_spinner(
        text=i18n("pets.chat.spinner.gemini_response"), show_time=True
    )

    for chunk in client.models.generate_content_stream(**gemini_api_config()):
        gemini_response_spinner.end()
        print(f"{chunk.text=}")
        if chunk.text is not None:
            this_response += chunk.text
            yield from str_stream(chunk.text)
        elif chunk.function_calls:
            function_calls.extend(chunk.function_calls)

    ctx_content.add_context(
        types.Content(role="model", parts=[types.Part.from_text(text=this_response)])
    )

    if function_calls:
        yield from gemini_function_calling(function_calls)


def chat_init(stream: Generator) -> None:
    ctx_content.add_context(
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=f"Introduce yourself briefly, including your role and what you can do. Language: {i18n.lang}."
                )
            ],
        )
    )

    full_response = st.chat_message("assistant").write_stream(stream)

    if isinstance(full_response, str):
        full_response = [full_response]

    for response in full_response:
        ctx_history.add_context({"role": "assistant", "content": response})

    ctx_content.clear_context()


def chat_bot():
    """
    Render the chat interface and process user input in Streamlit.

    Creates a bordered container to display chat history and a chat input field.
    When the user submits a message, calls chat() inside the same container to
    render and stream the assistant's response.
    """
    chat_container = st.container(border=True)
    with chat_container:
        if ctx_history.empty():
            chat_init(gemini_response_stream())
        else:
            display_chat_history(ctx_history)

    if prompt := st.chat_input(placeholder=input_field_placeholder, key="chat_bot"):
        ctx_content.add_context(
            types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
        )
        with chat_container:
            chat(ctx_history, prompt=prompt, stream=gemini_response_stream())


if __name__ == "__main__":
    page_init()
    chat_bot()
