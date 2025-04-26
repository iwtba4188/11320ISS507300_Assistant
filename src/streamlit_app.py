import streamlit as st
from bidict import bidict

from utils.i18n import i18n


def sidebar_name_to_page_title(pg_title: str) -> str:
    """
    Convert sidebar page labels to corresponding page titles based on i18n translations.

    Arguments:
        pg_title (str): The sidebar page label to convert

    Returns:
        str: The corresponding page title for the given sidebar label
    """
    if pg_title == i18n.get_message("sidebar.pet.chat.page_label"):
        return i18n.get_message("pet.chat.page_title")
    elif pg_title == i18n.get_message("sidebar.week10.2d.page_label"):
        return i18n.get_message("week10.2d.page_title")
    elif pg_title == i18n.get_message("sidebar.week10.3d.page_label"):
        return i18n.get_message("week10.3d.page_title")
    elif pg_title == i18n.get_message("sidebar.week10.skip_gram.page_label"):
        return i18n.get_message("week10.skip_gram.page_title")
    elif pg_title == i18n.get_message("sidebar.week10.cbow.page_label"):
        return i18n.get_message("week10.cbow.page_title")
    else:
        return pg_title


def setup_pages() -> None:
    """
    Configure and setup the Streamlit application pages.

    Sets up navigation with localized page titles, configures page settings,
    and runs the selected page.

    Returns:
        None
    """
    # TODO: When switching to the new page, the page title is flicking from
    #       `pet_sidebar_page_title` to `pet_page_config_page_title`.
    #
    #       One possible solution is to set the page name in the `navigation` function,
    #       but it is in the streamlit library.
    #       Related issue:
    #       https://github.com/streamlit/streamlit/issues/8388#issuecomment-2146227406
    #
    #       Another one is to use `st.page_link`, but it's not as convenient as
    #       `st.navigation`.
    pages = {
        i18n.get_message("sidebar.pet.section_label"): [
            st.Page(
                "pages/main_page.py",
                title=i18n.get_message("sidebar.pet.chat.page_label"),
                default=True,
            ),
        ],
        i18n.get_message("sidebar.week10.section_label"): [
            st.Page(
                "pages/word2vec-2d.py",
                title=i18n.get_message("sidebar.week10.2d.page_label"),
            ),
            st.Page(
                "pages/word2vec-3d.py",
                title=i18n.get_message("sidebar.week10.3d.page_label"),
            ),
            st.Page(
                "pages/word2vec-skip-gram.py",
                title=i18n.get_message("sidebar.week10.skip_gram.page_label"),
            ),
            st.Page(
                "pages/word2vec-cbow.py",
                title=i18n.get_message("sidebar.week10.cbow.page_label"),
            ),
        ],
    }

    pg = st.navigation(pages)

    st.set_page_config(
        page_title=sidebar_name_to_page_title(pg.title),
        layout="wide",
        initial_sidebar_state="auto",
        menu_items={
            "Get Help": "https://streamlit.io/",
            "Report a bug": "https://github.com/iwtba4188/11320ISS507300_Assistant",
            "About": i18n.get_message("menu_items.about"),
        },
        page_icon="img/favicon.ico",
    )

    pg.run()


def lang_code_text_conversion(lang: str) -> str:
    """
    Convert a language code to its corresponding text representation.

    Arguments:
        lang (str): The language code to convert

    Returns:
        str: The corresponding text representation of the language code
    """
    lang_code_text = bidict(
        {
            "default": "Default",
            "en": "English",
            "zh-TW": "繁體中文",
            "zh-CN": "简体中文",
        }
    )
    return lang_code_text.get(lang) or lang_code_text.inverse.get(lang)


def setup_lang() -> None:
    """
    Set the application language based on the user selection in the sidebar.

    Reads the selected language from the session state and configures
    the i18n module accordingly.

    Returns:
        None
    """
    # TODO: refector this mechanism to simplify the default language pipeline
    selected_lang_text = st.session_state.get("selected_lang_text", "Default")
    if selected_lang_text == "Default":
        i18n.set_to_default_lang()

    lang_setting = lang_code_text_conversion(selected_lang_text)

    i18n.set_lang(lang_setting)


def setup_sidebar() -> None:
    """
    Configure and display the application sidebar.

    Sets up the sidebar with a language selector that allows users to change
    the application language.

    Returns:
        None
    """
    lang_options = ["Default", "English", "繁體中文", "简体中文"]
    now_selected_lang_text = st.session_state.get("selected_lang_text", "Default")

    with st.sidebar:
        st.selectbox(
            "Language",
            lang_options,
            index=lang_options.index(now_selected_lang_text),
            on_change=setup_lang,
            key="selected_lang_text",
        )


if __name__ == "__main__":
    setup_lang()
    setup_pages()
    setup_sidebar()
