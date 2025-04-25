import json

from utils import read_file_content


def get_awaiting_adoption_pet_info() -> dict:
    """
    Provides information on pets that are currently seeking adoption.

    Returns:
        dict: A dictionary containing information about pets available for adoption.
    """
    print("get_awaiting_adoption_pet_info called!")
    animal_info = read_file_content("./src/static/animal_info.json")
    return json.loads(animal_info)
