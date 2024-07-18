import textwrap


def print_wrapped(
        text: str,
        width: int = 80,
    ):
    print(textwrap.fill(text, width))


def print_list(
        array: list,
    ):
    for item in array:
        print(item)