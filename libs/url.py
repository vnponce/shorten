import hashlib


def generate_url(url: str, size: int = 7, starting_index: int = 0) -> str:
    generated = to_shortcode(url, size, starting_index)
    return generated


def to_shortcode(url: str, size: int = 7, starting_index: int = 0) -> str:
    result = hashlib.md5(url.encode())
    final_index = starting_index + size
    return result.hexdigest()[starting_index:final_index]
