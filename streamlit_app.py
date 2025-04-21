import streamlit as st
import os
from google import genai
from google.genai import types

# from openai import OpenAI
import time

placeholderstr = "Please input your command"
user_name = "Shihtl"
user_image = "https://www.w3schools.com/howto/img_avatar.png"


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


def main():
    st.set_page_config(
        page_title="Assistant - The Residemy Agent",
        layout="wide",
        initial_sidebar_state="auto",
        menu_items={
            "Get Help": "https://streamlit.io/",
            "Report a bug": "https://github.com/iwtba4188/11320ISS507300_Assistant",
            "About": "This is a demo chatbot about your pets.",
        },
        page_icon="img/favicon.ico",
    )

    # Show title and description.
    st.title(f"💬 {user_name}'s Chatbot")

    with st.sidebar:
        selected_lang = st.selectbox("Language", ["English", "繁體中文"], index=1)
        if "lang_setting" in st.session_state:
            lang_setting = st.session_state["lang_setting"]
        else:
            lang_setting = selected_lang
            st.session_state["lang_setting"] = lang_setting

        st_c_1 = st.container(border=True)
        with st_c_1:
            st.image("https://www.w3schools.com/howto/img_avatar.png")

    st_c_chat = st.container(border=True)

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

    if prompt := st.chat_input(placeholder=placeholderstr, key="chat_bot"):
        chat(prompt)


if __name__ == "__main__":
    main()
