"""Business logic for greeting generation."""

MAX_NAME_LENGTH = 200


def process_greeting(name: str) -> str:
    """Turn a name string into a greeting.

    - Strips whitespace
    - Returns "Hello stranger!" for empty input
    - Truncates names longer than 200 characters
    """
    name = name.strip()

    if not name:
        return "Hello stranger!"

    if len(name) > MAX_NAME_LENGTH:
        name = name[:MAX_NAME_LENGTH] + "..."

    return f"Hello {name}!"
