import streamlit as st
import os
import google.generativeai as genai

# from openai import OpenAI
import time

placeholderstr = "Please input your command"
user_name = "Shihtl"
user_image = "https://www.w3schools.com/howto/img_avatar.png"


def stream_data(stream_str):
    for word in stream_str.split(" "):
        yield word + " "
        time.sleep(0.15)


def read_system_prompt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as file:
        system_prompt = file.read()
    return system_prompt


def generate_response_gemini(prompt: str) -> str:

    system_prompt = read_system_prompt("./system_prompt.txt")

    genai.configure(api_key=st.secrets["gemini_api_key"])

    # Create the model
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 65536,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash-preview-04-17",
        generation_config=generation_config,
        system_instruction=system_prompt,
    )

    chat_session = model.start_chat()

    response = chat_session.send_message(prompt)

    print(response.text)

    return response.text


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
