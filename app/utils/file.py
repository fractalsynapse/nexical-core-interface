import base64


def get_file_content(file):
    handle = None
    content = ""
    try:
        handle = file.open("rb")
        content = base64.b64encode(handle.read())
    finally:
        if handle:
            handle.close()
    return content
