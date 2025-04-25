import os
import time

import streamlit as st

from google import genai
from google.genai import types
from utils.i18n import i18n


input_field_placeholder = i18n.get_message("pet.chat.input_placeholder")
user_name = "Shihtl"
user_image = "https://www.w3schools.com/howto/img_avatar.png"


def page_init() -> None:
    # Show title and description.
    st.title(i18n.get_message("pet.chat.doc_title").format(user_name=user_name))


def stream_data(stream_str):
    for word in stream_str.split(" "):
        yield word + " "
        time.sleep(0.15)


def read_file_content(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as file:
        file_content = file.read()
    return file_content


def generate_response_gemini(prompt: str) -> str:

    system_prompt = read_file_content("./static/system_prompt.txt")

    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    animal_adoption_file = f'animal info for adoption: {read_file_content("./static/animal_info.json")}\n\n'

    model = "gemini-2.5-flash-preview-04-17"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=0,
        response_mime_type="text/plain",
        system_instruction=[
            # TODO: better usage method of `animal_adoption_file`
            types.Part.from_text(text=animal_adoption_file),
            types.Part.from_text(text=system_prompt),
        ],
    )

    generate_content = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )

    return generate_content.text


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

        response = generate_response_gemini(prompt)
        # response = f"You type: {prompt}"
        st.session_state.messages.append({"role": "assistant", "content": response})
        st_c_chat.chat_message("assistant").write_stream(stream_data(response))

    if prompt := st.chat_input(placeholder=input_field_placeholder, key="chat_bot"):
        chat(prompt)


if __name__ == "__main__":
    page_init()
    chat_bot()
