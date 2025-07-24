import re


def snake_case(name: str) -> str:
    """Convert a string to snake_case."""
    s = re.sub(r"[\s\-]+", "_", name)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    s = re.sub(r"([a-zA-Z])([0-9])", r"\1_\2", s)
    s = re.sub(r"([0-9])([a-zA-Z])", r"\1_\2", s)
    return s.lower()
