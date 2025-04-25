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

        # TODO: Using logging instead of print statements
        print(f"Current language: {self._lang}")
        print(f"Default language: {self._default_lang}")
        print(f"Available languages: {self.get_valid_languages()}")

    def _validate_translations(self) -> None:
        """
        Validate that translation files exist and meet required format.

        Raises:
            FileNotFoundError: If no translation files are found

        Returns:
            None
        """
        if not self._translations:
            raise FileNotFoundError(
                f"Could not find any translation files in {self._i18n_folder_path}"
            )

        # TODO: Implement validation logic for translations
        pass

    def _build_translations(self) -> dict:
        """
        Build a dictionary of translations from JSON files in the i18n folder.

        Scans the i18n folder path for `messages.json` files and loads them into a dictionary
        where keys are language codes.

        Returns:
            dict: Dictionary of translations with language codes as keys
        """
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
        """
        Set the current language for translations.

        If the specified language is not available, falls back to the default language.

        Arguments:
            language (str): Language code to set as current language

        Returns:
            None
        """
        if language in self._translations.keys():
            self._lang = language
        else:
            self._lang = self._default_lang

    def set_to_default_lang(self) -> None:
        """
        Reset the current language to the default language.

        Returns:
            None
        """
        self._lang = self._default_lang

    def get_default_lang(self) -> str:
        """
        Get the default language code.

        Returns:
            str: The default language code
        """
        return self._default_lang

    def get_valid_languages(self) -> list[str]:
        """
        Get a list of all valid language codes available for translation.

        Returns:
            list[str]: List of available language codes
        """
        return list(self._translations.keys())

    def get_message(self, key: str) -> str:
        """
        Get a translated message for the given key.

        Attempts to find the translation in the current language first, then falls back
        to the default language if not found. Raises an error if the key doesn't exist in either.

        Arguments:
            key (str): The translation key to look up

        Returns:
            str: The translated message text

        Raises:
            KeyError: If the key is not found in any language
        """
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
