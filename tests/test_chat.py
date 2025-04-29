import os
from unittest.mock import PropertyMock

import streamlit as st
from pytest_mock import MockFixture
from streamlit.testing.v1 import AppTest


def test_chat(mocker: MockFixture) -> None:
    # patch the property on the class
    mocker.patch.object(
        type(st.context), "locale", new_callable=PropertyMock, return_value="en"
    )

    at = AppTest.from_file("../src/streamlit_app.py", default_timeout=60).run()
    at.secrets["gemini_api_key"] = os.getenv("GEMINI_API_KEY")

    # check simple chat
    prompt = "你好，我想領養一隻貓，幫我查詢目前等待領養的貓咪資訊（非常簡短的），我住公寓，家裡只有我，我會長時間在家，極度簡短的回答。"
    at.chat_input(key="chat_bot").set_value(prompt).run()

    assert len(at.chat_message) >= 2
    assert at.chat_message[0].children[0].value == prompt

    # check history print
    prompt = "沒問題，我會參考你給的結果，謝謝你"
    at.chat_input(key="chat_bot").set_value(prompt).run()
    assert len(at.chat_message) >= 4
    assert at.chat_message[2].children[0].value == prompt

    assert not at.exception
