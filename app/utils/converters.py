# placeholder
from typing import List


def list_to_string(items: List[str]) -> str:
    return ", ".join(items)


def string_to_list(text: str) -> List[str]:
    return [item.strip() for item in text.split(",") if item.strip()]