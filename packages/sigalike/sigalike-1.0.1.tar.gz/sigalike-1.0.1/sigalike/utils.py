from typing import Any


def check_input_type(obj: Any, target_type: type) -> None:

    if not isinstance(obj, target_type):
        raise TypeError(f"Input {obj} is the wrong type. Expected {target_type}")


def check_content(s: str) -> None:

    if s.strip() == "":
        raise ValueError("Input string must have content.")
