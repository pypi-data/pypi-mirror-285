import re
from pathlib import Path


def clean_text(text):
    num, text = text.split("_", maxsplit=1)
    return f"{int(num)}) {text.replace('_', ' ').capitalize()}"


def extract_leading_numbers(text):
    m = re.match(r"^\d+", text)
    if m:
        return int(m.group())


def text_border(text, symbol="=", side_symbol="=", padding=1):
    width = 2 * padding + len(text) + 2
    top = bottom = f"{symbol * width}"
    pad = " " * padding
    return f"{top}\n{side_symbol}{pad}{text}{pad}{side_symbol}\n{bottom}"


def tree(dir_path: Path, prefix: str = ""):
    """A recursive generator, given a directory Path object
    will yield a visual tree structure line by line
    with each line prefixed by the same characters
    """
    # prefix components:
    space = "    "
    branch = "│   "
    # pointers:
    tee = "├── "
    last = "└── "

    contents = list(dir_path.iterdir())
    # contents each get pointers that are ├── with a final └── :
    pointers = [tee] * (len(contents) - 1) + [last]
    for pointer, path in zip(pointers, contents):
        if path.name.endswith(".pyc") or "__pycache__" in path.name:
            continue
        yield prefix + pointer + path.name
        if path.is_dir():  # extend the prefix and recurse:
            extension = branch if pointer == tee else space
            # i.e. space because last, └── , above so no more |
            yield from tree(path, prefix=prefix + extension)
