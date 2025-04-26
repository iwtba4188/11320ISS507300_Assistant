import streamlit as st


# [Files]
def read_file_content(file_path: str) -> str:
    """
    Read and return the content of a text file.

    Arguments:
        file_path (str): Path to the file to be read

    Returns:
        str: Content of the file as a string
    """
    with open(file_path, "r", encoding="utf-8") as file:
        file_content = file.read()
    return file_content


# [Badges]
def info_badge(msg: str) -> str:
    """
    Generate an info badge message.

    Arguments:
        msg (str): The message to display in the badge

    Returns:
        str: The formatted info badge message
    """
    return f"\n:blue-badge[:material/info: {msg}]\n\n"


def success_badge(msg: str) -> str:
    """
    Generate a success badge message.

    Arguments:
        msg (str): The message to display in the badge

    Returns:
        str: The formatted success badge message
    """
    return f"\n:green-badge[:material/check: {msg}]\n\n"


def error_badge(msg: str) -> str:
    """
    Generate an error badge message.

    Arguments:
        msg (str): The message to display in the badge

    Returns:
        str: The formatted error badge message
    """
    return f"\n:red-badge[:material/error: {msg}]\n\n"


# [Streamlit Spinner]
class st_spinner:
    # ref: https://github.com/streamlit/streamlit/issues/6799#issuecomment-1578395288
    def __init__(self, text="In progress...", show_time=False):
        self.text = text
        self.show_time = show_time
        self._spinner = iter(self._start())  # This creates an infinite spinner
        next(self._spinner)  #  This starts it

    def _start(self):
        with st.spinner(self.text, show_time=self.show_time):
            yield

    def end(self):  # This ends it
        next(self._spinner, None)


# # Usage
# s = st_spinner()
# time.sleep(5)
# s.end()
