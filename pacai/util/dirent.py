import atexit
import os
import shutil
import tempfile
import uuid

def get_temp_path(prefix = '', suffix = '', rm = True):
    """
    Get a path to a valid (but not currently existing) temp dirent.
    If rm is True, then the dirent will be attempted to be deleted on exit
    (no error will occur if the path is not there).
    """

    path = None
    while ((path is None) or os.path.exists(path)):
        path = os.path.join(tempfile.gettempdir(), prefix + str(uuid.uuid4()) + suffix)

    if (rm):
        atexit.register(remove, path)

    return path

def remove(path):
    if (not os.path.exists(path)):
        return

    if (os.path.isfile(path) or os.path.islink(path)):
        os.remove(path)
    elif (os.path.isdir(path)):
        shutil.rmtree(path)
    else:
        raise ValueError("Unknown type of dirent: '%s'." % (path))

def move(source, dest):
    shutil.move(source, dest)

def copy(source, dest, dirs_exist_ok = False):
    """
    Copy a file or directory into dest.
    If source is a file, then dest can be a file or dir.
    If source is a dir, it is copied as a subdirectory of dest.
    If dirs_exist_ok is true, an existing destination directory is allowed.
    """

    if (os.path.isfile(source)):
        try:
            os.makedirs(os.path.dirname(dest), exist_ok = True)
            shutil.copy2(source, dest)
        except shutil.SameFileError:
            return
    else:
        if (os.path.isdir(dest)):
            dest = os.path.join(dest, os.path.basename(source))

        shutil.copytree(source, dest, dirs_exist_ok = dirs_exist_ok)

def copy_contents(source, dest):
    """
    Copy a file or the contents of a directory (excluding the top-level directory) into dest.
    For a file: `cp source dest/`
    For a dir: `cp -r source/* dest/`
    """

    source = os.path.abspath(source)

    if (os.path.isfile(source)):
        shutil.copy2(source, dest)
        return

    for dirent in os.listdir(source):
        source_path = os.path.join(source, dirent)
        dest_path = os.path.join(dest, dirent)

        if (os.path.isfile(source_path)):
            shutil.copy2(source_path, dest_path)
        else:
            shutil.copytree(source_path, dest_path)
