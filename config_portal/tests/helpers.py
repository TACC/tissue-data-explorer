import base64
import magic
from pathlib import Path, PosixPath
import shutil


def make_upload_content(filepath):
    # open the file
    with open(filepath, "rb") as file:
        filebytes = file.read()
    b64bytes = base64.b64encode(filebytes)
    b64str = b64bytes.decode("utf-8")

    # get the mime type
    mime = magic.from_buffer(b64bytes, mime=True)
    content_type = "".join(["data:", mime, ";base64"])

    # join the type and content strings
    content = "".join([content_type, ",", b64str])
    return content


def decode_str(b64str):
    t1, s1 = b64str.split(",")
    return base64.b64decode(s1)


def clean_dir(path_str: str) -> tuple[bool, str]:
    """
    Deletes and recreates the provided directory, if it is a directory, or its parent, if the path points to a file.

    Returns (operation succeeded, error message)
    """
    try:
        p = Path(path_str)
        if not Path.is_dir(p):
            depot_dir = PosixPath(p.parent)
        else:
            depot_dir = PosixPath(p)
        shutil.rmtree(depot_dir)
        Path.mkdir(depot_dir)
        return (True, "")
    except Exception as err:
        return (False, f"{err}")
