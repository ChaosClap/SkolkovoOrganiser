import re

def is_valid_credential(text: str) -> bool:
    """Проверка: только латинские буквы и цифры"""
    return bool(re.fullmatch(r"[a-zA-Z0-9]+", text.strip()))

def is_not_empty(text: str) -> bool:
    """Проверка: не пустая строка (без пробелов)"""
    return bool(text.strip())


def is_min_length(value: str, min_length: int) -> bool:
    return len(value.strip()) >= min_length