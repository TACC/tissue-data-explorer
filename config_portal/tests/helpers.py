import base64
import magic


def make_upload_content(filepath):
    # open the file
    with open(filepath, "rb") as file:
        filebytes = file.read()
    b64bytes = base64.b64encode(filebytes)
    b64str = b64bytes.decode("utf-8")

    # get the mime type
    mime = magic.from_buffer(b64bytes, mime=True)
    print(mime)
    content_type = "".join(["data:", mime, ";base64"])

    # join the type and content strings
    content = "".join([content_type, ",", b64str])
    return content


def decode_str(b64str):
    t1, s1 = b64str.split(",")
    return base64.b64decode(s1)
