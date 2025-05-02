DEFAULT_ENCODING: str = 'utf-8'

def read(path: str, strip: bool = True, encoding: str = DEFAULT_ENCODING) -> str:
    """ Read the given file into a string. """

    with open(path, 'r', encoding = encoding) as file:
        contents = file.read()

    if (strip):
        contents = contents.strip()

    return contents

def write(path: str,
        contents: str | None,
        strip: bool = True,
        newline: bool = True,
        encoding: str = DEFAULT_ENCODING) -> None:
    """ Write the given content into a file. """

    if (contents is None):
        contents = ''

    if (strip):
        contents = contents.strip()

    if (newline):
        contents += "\n"

    with open(path, 'w', encoding = encoding) as file:
        file.write(contents)
