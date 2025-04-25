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
