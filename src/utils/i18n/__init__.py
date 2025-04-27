import streamlit as st

from .internationalization import I18n

i18n = I18n(lang=st.context.locale, default_lang=st.context.locale)
