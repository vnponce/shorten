import hashlib

DEFAULT_SHORT_CODE_SIZE = 7


def generate_url(url: str, size: int = DEFAULT_SHORT_CODE_SIZE, starting_index: int = 0) -> str:
    result = hashlib.md5(url.encode())
    final_index = starting_index + size
    return result.hexdigest()[starting_index:final_index]


def move_one_place_to_the_right(starting_index: int, string: str, size: int = DEFAULT_SHORT_CODE_SIZE) -> str:
    starting_index += 1
    final_index = size + starting_index
    return string[starting_index:final_index]
