import os
import time
from typing import Generator

import streamlit as st

from google import genai
from google.genai import types

from utils.function_call import get_awaiting_adoption_pet_info
from utils.helpers import read_file_content, success_badge, error_badge, info_badge
from utils.i18n import i18n


input_field_placeholder = i18n.get_message("pet.chat.input_placeholder")
user_name = "Shihtl"
user_image = "https://www.w3schools.com/howto/img_avatar.png"


def page_init() -> None:
    """
    Initialize the page by setting the title with the user's name.

    Returns:
        None
    """
    st.title(i18n.get_message("pet.chat.doc_title").format(user_name=user_name))


def str_stream(text: str) -> Generator:
    """
    Yield each character in the string with a small delay to create a typing effect.

    Arguments:
        text (str): The text to stream character by character

    Returns:
        Generator: A generator yielding individual characters
    """
    for char in text:
        yield char
        time.sleep(0.005)


def gen_gemini_configs(prompt: str) -> dict:
    """
    Generate configuration dictionary for Gemini API call.

    Arguments:
        prompt (str): The user's input prompt to send to the model

    Returns:
        dict: Configuration dictionary containing model, contents, and config settings for the Gemini API
    """
    system_prompt = read_file_content("./src/static/system_prompt.txt")

    model = "gemini-2.5-flash-preview-04-17"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt),
            ],
        ),
    ]
    tools = [get_awaiting_adoption_pet_info]

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
        tools=tools,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )

    return {
        "model": model,
        "contents": contents,
        "config": generate_content_config,
    }


def function_calling(func_call_name: str) -> dict:
    """
    Call the specified function and handle any exceptions.

    Arguments:
        func_call_name (str): The name of the function to call

    Returns:
        dict: A dictionary containing the status and result of the function call
    """

    status = ""

    try:
        if func_call_name == "get_awaiting_adoption_pet_info":
            result = get_awaiting_adoption_pet_info()
        else:
            raise ValueError(f"Unknown function call: {func_call_name}")
    except Exception as e:
        status = "error"
        result = str(e)
    else:
        status = "success"

    return {
        "status": status,
        "result": result,
    }


def gemini_function_calling(
    st_c_chat,
    gemini_configs: dict,
    function_calls: list[types.FunctionCall],
) -> Generator:
    """
    Handle function calling and response streaming for Gemini API.

    Arguments:
        st_c_chat: Streamlit chat container to display messages
        gemini_configs (dict): Configuration dictionary for Gemini API
        function_calls (list[types.FunctionCall]): List of function calls to process

    Returns:
        Generator: Yields response stream text
    """

    for func_call in function_calls:
        spinner_func_call_text = i18n.get_message(
            "pet.chat.spinner.func_call_text"
        ).format(func_call_name=func_call.name)

        with (
            st_c_chat,
            st.spinner(spinner_func_call_text, show_time=True),
        ):
            func_call_result = function_calling(func_call.name)

            function_response_part = types.Part.from_function_response(
                name=func_call.name,
                response={"result": func_call_result["result"]},
            )
            gemini_configs["contents"].append(
                types.Content(role="model", parts=[types.Part(function_call=func_call)])
            )
            gemini_configs["contents"].append(
                types.Content(role="user", parts=[function_response_part])
            )

            time.sleep(1)

        func_call_msg_i18n_key = (
            f"pet.chat.badge.func_call_{func_call_result['status']}"
        )
        func_call_msg = i18n.get_message(func_call_msg_i18n_key).format(
            func_name=func_call.name
        )

        if func_call_result["status"] == "error":
            yield from str_stream(error_badge(func_call_msg))
        else:
            yield from str_stream(success_badge(func_call_msg))

    think_again_msg = i18n.get_message("pet.chat.badge.think_again")
    yield from str_stream(info_badge(think_again_msg))

    yield from gemini_response_stream(st_c_chat, gemini_configs)


def gemini_response_stream(st_c_chat, gemini_configs: dict) -> Generator:
    """
    Stream responses from the Gemini model and handle any function calls.

    Arguments:
        st_c_chat: Streamlit chat container to display messages
        gemini_configs (dict): Configuration dictionary for Gemini API

    Returns:
        Generator: Yields response stream text and processes any function calls
    """

    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    function_calls = []
    this_response = ""

    for chunk in client.models.generate_content_stream(**gemini_configs):
        print(f"{chunk.text=}")
        if chunk.text is not None:
            this_response += chunk.text
            yield from str_stream(chunk.text)
        elif chunk.function_calls:
            function_calls.extend(chunk.function_calls)

    gemini_configs["contents"].append(
        types.Content(role="model", parts=[types.Part.from_text(text=this_response)])
    )

    if function_calls:
        yield from gemini_function_calling(st_c_chat, gemini_configs, function_calls)


def chat_bot():
    """
    Initialize and manage the chat interface with the Gemini model.

    This function sets up the chat container, displays chat history,
    and defines an inner function to handle user inputs and model responses.

    Returns:
        None
    """

    # Chat section container
    st_c_chat = st.container(border=True)

    # Show chat history in this session
    if "history" not in st.session_state:
        st.session_state.history = []
    histories = st.session_state.get("history", [])
    for history in histories:
        print(history)
        avatar = user_image if history["role"] == "user" else None
        with st_c_chat.chat_message(history["role"], avatar=avatar):
            st.markdown((history["content"]))

    def chat(prompt: str):
        """
        Process user input and generate model response.

        Arguments:
            prompt (str): User input text to send to the model

        Returns:
            None
        """
        st_c_chat.chat_message("user", avatar=user_image).write(prompt)
        st.session_state.history.append({"role": "user", "content": prompt})

        gemini_configs = gen_gemini_configs(prompt)
        full_response = st_c_chat.chat_message("assistant").write_stream(
            gemini_response_stream(st_c_chat, gemini_configs)
        )

        if isinstance(full_response, str):
            full_response = [full_response]

        # Check if the response is a list (for function calls)
        for response in full_response:
            st.session_state.history.append({"role": "assistant", "content": response})

        print(full_response)

    if prompt := st.chat_input(placeholder=input_field_placeholder, key="chat_bot"):
        chat(prompt)


if __name__ == "__main__":
    page_init()
    chat_bot()
