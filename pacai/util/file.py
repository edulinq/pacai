def read(path, strip = True):
    with open(path, 'r') as file:
        contents = file.read()

    if (strip):
        contents = contents.strip()

    return contents

def write(path, contents, strip = True, newline = True):
    if (contents is None):
        contents = ''

    if (strip):
        contents = contents.strip()

    if (newline):
        contents += "\n"

    with open(path, 'w') as file:
        file.write(contents)
