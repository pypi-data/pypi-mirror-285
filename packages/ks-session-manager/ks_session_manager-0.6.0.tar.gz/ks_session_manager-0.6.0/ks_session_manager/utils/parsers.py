from typing import Optional


def parse_none_if_null_str(value: str) -> Optional[str]:
    if value is None:
        return None

    if isinstance(value, str):
        if value == 'None' or value == 'null' or value:
            return None

    return value
