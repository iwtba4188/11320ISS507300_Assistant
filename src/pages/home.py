import streamlit as st


def page_init() -> None:
    st.title("Welcome to the Pet Adoption App")
    st.write("This app is designed to help you find your perfect pet!")


if __name__ == "__main__":
    page_init()
