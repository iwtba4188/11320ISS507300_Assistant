import streamlit as st

from utils.function_call.pets import test_cawling_dcard_urls


def page_init() -> None:
    st.title("Welcome to the Pet Adoption App")
    st.write("This app is designed to help you find your perfect pet!")


if __name__ == "__main__":
    page_init()
    test_cawling_dcard_urls()
