import streamlit as st


class I18n:
    """
    A class to handle internationalization (i18n) for a Streamlit application.

    It loads translation files from a specified folder and provides methods to
    get translated messages.

    Attributes:
        lang (str): The current language code.
        default_lang (str): The default language code. If is `"streamlit"`, it will be set to the current locale.
        i18n_folder_path (str): The path to the folder containing translation files.
    """

    def __init__(
        self,
        lang: str = None,
        default_lang: str = "streamlit",
        i18n_folder_path: str = "./_locales",
    ) -> None:
        self._i18n_folder_path = i18n_folder_path
        self._translations = self._build_translations()
        self._validate_translations()

        if default_lang == "streamlit":
            self._default_lang = st.context.locale
        else:
            self._default_lang = default_lang
        self._lang = lang if lang else default_lang
        self.set_lang(self._lang)

        print(f"Current language: {self._lang}")
        print(f"Default language: {self._default_lang}")
        print(f"Available languages: {self.get_valid_languages()}")

    def _validate_translations(self) -> None:
        if not self._translations:
            raise FileNotFoundError(
                f"Could not find any translation files in {self._i18n_folder_path}"
            )

        # TODO: Implement validation logic for translations
        pass

    def _build_translations(self) -> None:
        import os
        import json

        translations = {}
        for root, dirs, files in os.walk(self._i18n_folder_path):
            print(f"Checking {root}...")
            if "messages.json" in files:
                lang = os.path.basename(root)
                with open(
                    os.path.join(root, "messages.json"), "r", encoding="utf-8"
                ) as f:
                    translations[lang] = json.load(f)

        return translations

    def set_lang(self, language: str) -> None:
        if language in self._translations.keys():
            self._lang = language
        else:
            self._lang = self._default_lang

    def set_to_default_lang(self) -> None:
        self._lang = self._default_lang

    def get_default_lang(self) -> str:
        return self._default_lang

    def get_valid_languages(self) -> list[str]:
        return list(self._translations.keys())

    def get_message(self, key: str) -> str:
        try:
            return self._translations[self._lang][key]["message"]
        except KeyError:
            try:
                return self._translations[self._default_lang][key]["message"]
            except KeyError:
                raise KeyError(f"Missing translation for key: {key}")


if __name__ == "__main__":
    i18n = I18n(lang="en", i18n_folder_path="../../../_locales")
    print(i18n.get_valid_languages())
    print(i18n.get_message("page_config_menu_items_About"))
