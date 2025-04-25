import os
import time

import streamlit as st

from google import genai
from google.genai import types

from utils.function_call import get_awaiting_adoption_pet_info
from utils import read_file_content
from utils.i18n import i18n


input_field_placeholder = i18n.get_message("pet.chat.input_placeholder")
user_name = "Shihtl"
user_image = "https://www.w3schools.com/howto/img_avatar.png"


def page_init() -> None:
    # Show title and description.
    st.title(i18n.get_message("pet.chat.doc_title").format(user_name=user_name))


def gemini_response_stream(prompt: str):

    system_prompt = read_file_content("./src/static/system_prompt.txt")

    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

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
        thinking_config=types.ThinkingConfig(
            thinking_budget=1000,
        ),
        response_mime_type="text/plain",
        system_instruction=[
            types.Part.from_text(text=system_prompt),
        ],
        tools=tools,
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        # print(f"{chunk.text=}")
        # print(f"{chunk.automatic_function_calling_history=}")

        yield chunk.text


def chat_bot():

    # Chat section container
    st_c_chat = st.container(border=True)

    # Show chat history in this session
    if "messages" not in st.session_state:
        st.session_state.messages = []
    else:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                if user_image:
                    st_c_chat.chat_message(msg["role"], avatar=user_image).markdown(
                        (msg["content"])
                    )
                else:
                    st_c_chat.chat_message(msg["role"]).markdown((msg["content"]))
            elif msg["role"] == "assistant":
                st_c_chat.chat_message(msg["role"]).markdown((msg["content"]))
            else:
                try:
                    image_tmp = msg.get("image")
                    if image_tmp:
                        st_c_chat.chat_message(msg["role"], avatar=image_tmp).markdown(
                            (msg["content"])
                        )
                except:
                    st_c_chat.chat_message(msg["role"]).markdown((msg["content"]))

    # Chat function section (timing included inside function)
    def chat(prompt: str):
        st_c_chat.chat_message("user", avatar=user_image).write(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        full_response = st_c_chat.chat_message("assistant").write_stream(
            gemini_response_stream(prompt)
        )
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )

    if prompt := st.chat_input(placeholder=input_field_placeholder, key="chat_bot"):
        chat(prompt)


if __name__ == "__main__":
    page_init()
    chat_bot()
