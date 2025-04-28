class I18n:
    def __init__(
        self,
        lang: str,
        i18n_folder_path: str = "./_locales",
    ) -> None:
        self._i18n_folder_path = i18n_folder_path
        self._translations = self._build_translations()
        self._validate_translations()

        self._lang = ""
        self._default_lang = ""
        self.set_default_lang("en")
        self.set_lang(lang)

    def __call__(self, key: str) -> str:
        return self.get_message(key)

    def _validate_translations(self) -> None:
        if not self._translations:
            raise FileNotFoundError(
                f"Could not find any translation files in {self._i18n_folder_path}"
            )

    def _build_translations(self) -> dict:
        import json
        import os

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

    def is_valid_lang(self, lang: str) -> bool:
        return self.match_lang(lang) is not None

    def set_lang(self, lang: str) -> None:
        self._lang = self.match_lang(lang)
        if self._lang is None:
            self.set_to_default_lang()
            print(
                f"Invalid language '{lang}' specified. Falling back to default language '{self._default_lang}'."
            )

    def set_to_default_lang(self) -> None:
        self._lang = self._default_lang

    def match_lang(self, lang: str) -> str | None:
        valid_langs = self.get_valid_languages()
        valid_langs = list(filter(lambda x: lang.startswith(x), valid_langs))

        return sorted(valid_langs, reverse=True)[0] if valid_langs else None

    def get_message(self, key: str) -> str:
        possible_langs = [self._lang, self._default_lang, "en"]

        for lang in possible_langs:
            if res := self._translations.get(lang, {}).get(key, {}).get("message"):
                return res

        raise KeyError(
            f"Missing translation for key: {key} (lang: {self._lang}, default_lang: {self._default_lang}, 'en')"
        )
