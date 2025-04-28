from unittest.mock import PropertyMock

import pytest
import streamlit as st
from pytest_mock import MockFixture
from streamlit.testing.v1 import AppTest

from utils.i18n import I18n

i18n = I18n(lang="en")


@pytest.mark.parametrize(
    "init_lang",
    ["en", "en-US", "zh-TW", "zh-CN", "zh-HK"],
)
@pytest.mark.parametrize(
    "page_path",
    ["word2vec-2d", "word2vec-3d", "word2vec-skip-gram", "word2vec-cbow"],
)
def test_page_diff_langs(mocker: MockFixture, page_path: str, init_lang: str) -> None:
    # patch the property on the class
    mocker.patch.object(
        type(st.context), "locale", new_callable=PropertyMock, return_value=init_lang
    )

    at = AppTest.from_file("../src/streamlit_app.py", default_timeout=10).run()
    at.switch_page(f"./pages/{page_path}.py").run()

    print(at.title[0].value)
    print(at.selectbox)

    assert not at.exception


@pytest.mark.parametrize(
    "select_lang",
    ["browser_default", "en", "zh-TW", "zh-CN"],
)
def test_lang_selection(mocker: MockFixture, select_lang: str) -> None:
    i18n.set_lang(select_lang)

    # patch the property on the class
    mocker.patch.object(
        type(st.context), "locale", new_callable=PropertyMock, return_value="en"
    )

    at = AppTest.from_file("../src/streamlit_app.py", default_timeout=10).run()

    # print(f"Before: {at.chat_input[0].placeholder=}")
    at.selectbox(key="selected_lang").select(select_lang).run()
    # print(f"After: {at.chat_input[0].placeholder=}")
    # print(f"Ans: {i18n('pet.chat.input_placeholder')=}")

    assert at.chat_input[0].placeholder == i18n("pet.chat.input_placeholder")

    assert not at.exception


# XXX: it's not possible to test the data_editor
#      in the current version of streamlit (1.44.0)
# @pytest.mark.parametrize(
#     "page_path",
#     ["word2vec-2d", "word2vec-3d", "word2vec-skip-gram", "word2vec-cbow"],
# )
# def test_week10(mocker: MockFixture, page_path: str) -> None:
# import pandas as pd
# from src.utils.week10.helpers import df_input
#     # patch the property on the class
#     mocker.patch.object(
#         type(st.context), "locale", new_callable=PropertyMock, return_value="en"
#     )

#     at = AppTest.from_file("../src/streamlit_app.py", default_timeout=10).run()
#     at.switch_page(f"./pages/{page_path}.py").run()

#     assert at.warning[0].value == i18n("week10.no_sentences")

#     at.get("data_editor")

#     assert not at.exception


# @pytest.mark.parametrize(
#     "page_path",
#     [
#         "word2vec-2d",
#         # "word2vec-3d",
#         # "word2vec-skip-gram",
#         # "word2vec-cbow",
#     ],
# )
# def test_week10(mocker: MockFixture, page_path: str) -> None:
#     # patch the property on the class
#     mocker.patch.object(
#         type(st.context), "locale", new_callable=PropertyMock, return_value="en"
#     )

#     mock_df_input_return_value_with_valid_sentences = pd.DataFrame(
#         [
#             {"selected": True, "sentence": "Sample sentence"},
#             {"selected": True, "sentence": "Another sentence"},
#         ],
#         columns=["selected", "sentence"],
#     )

#     at = AppTest.from_file("../src/streamlit_app.py", default_timeout=10).run()
#     at.switch_page(f"./pages/{page_path}.py").run()

#     assert at.warning[0].value == i18n("week10.no_sentences")

#     at.dataframe[0].set_value(mock_df_input_return_value_with_valid_sentences).run()

#     assert not at.exception
