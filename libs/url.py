import hashlib


def generate_url(url: str, size: int = 7) -> str:
    generated = to_shortcode(url, size)
    return generated


def to_shortcode(url: str, size: int) -> str:
    result = hashlib.md5(url.encode())
    return result.hexdigest()[:size]
