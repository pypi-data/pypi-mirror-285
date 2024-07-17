from io import BytesIO

from pyrogram.raw.core.primitives import Int, Long, Int128, Int256, Bool, Bytes, String, Double, Vector
from pyrogram.raw.core import TLObject
from pyrogram import raw
from typing import List, Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


class CheckQuickReplyShortcut(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``184``
        - ID: ``F1D0FBD3``

    Parameters:
        shortcut (``str``):
            N/A

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["shortcut"]

    ID = 0xf1d0fbd3
    QUALNAME = "functions.messages.CheckQuickReplyShortcut"

    def __init__(self, *, shortcut: str) -> None:
        self.shortcut = shortcut  # string

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "CheckQuickReplyShortcut":
        # No flags
        
        shortcut = String.read(b)
        
        return CheckQuickReplyShortcut(shortcut=shortcut)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(String(self.shortcut))
        
        return b.getvalue()
