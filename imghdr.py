import os
from typing import Optional, Union, BinaryIO


"""
Compatibility shim for Python 3.13+

The standard library imghdr module was removed in Python 3.13, but
older versions of Streamlit still import it. This minimal
reimplementation provides the imghdr.what function used by Streamlit.
"""


FileArg = Union[str, bytes, os.PathLike, BinaryIO]


def what(file: FileArg, h: Optional[bytes] = None) -> Optional[str]:
    """
    Roughly compatible with the old imghdr.what interface.

    - file: filename, path-like, or binary file object
    - h: optional bytes header; if not provided, this function will
      read up to 32 bytes from the file.

    Returns a short string like 'png', 'gif', 'jpeg', 'bmp', or None
    if the type cannot be determined.
    """
    if h is None:
        if isinstance(file, (str, bytes, os.PathLike)):
            with open(file, "rb") as f:  # type: ignore[arg-type]
                h = f.read(32)
        else:
            # Assume it's a file-like object
            f = file  # type: ignore[assignment]
            pos = f.tell()
            h = f.read(32)
            f.seek(pos)

    if not h:
        return None

    # PNG
    if h.startswith(b"\211PNG\r\n\032\n"):
        return "png"

    # GIF
    if h[:6] in (b"GIF87a", b"GIF89a"):
        return "gif"

    # JPEG (JFIF / Exif)
    if len(h) >= 10 and h[6:10] in (b"JFIF", b"Exif"):
        return "jpeg"

    # BMP
    if h.startswith(b"BM"):
        return "bmp"

    return None

