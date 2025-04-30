def read(path: str, strip: bool = True) -> str:
    with open(path, 'r') as file:
        contents = file.read()

    if (strip):
        contents = contents.strip()

    return contents

def write(path: str, contents: str | None, strip: bool = True, newline: bool = True) -> None:
    if (contents is None):
        contents = ''

    if (strip):
        contents = contents.strip()

    if (newline):
        contents += "\n"

    with open(path, 'w') as file:
        file.write(contents)
