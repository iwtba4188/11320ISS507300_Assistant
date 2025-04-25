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
