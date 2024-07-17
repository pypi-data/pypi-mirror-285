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


class WebViewResultUrl(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyrogram.raw.base.WebViewResult`.

    Details:
        - Layer: ``184``
        - ID: ``4D22FF98``

    Parameters:
        url (``str``):
            N/A

        fullsize (``bool``, *optional*):
            N/A

        query_id (``int`` ``64-bit``, *optional*):
            N/A

    Functions:
        This object can be returned by 3 functions.

        .. currentmodule:: pyrogram.raw.functions

        .. autosummary::
            :nosignatures:

            messages.RequestWebView
            messages.RequestSimpleWebView
            messages.RequestAppWebView
    """

    __slots__: List[str] = ["url", "fullsize", "query_id"]

    ID = 0x4d22ff98
    QUALNAME = "types.WebViewResultUrl"

    def __init__(self, *, url: str, fullsize: Optional[bool] = None, query_id: Optional[int] = None) -> None:
        self.url = url  # string
        self.fullsize = fullsize  # flags.1?true
        self.query_id = query_id  # flags.0?long

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "WebViewResultUrl":
        
        flags = Int.read(b)
        
        fullsize = True if flags & (1 << 1) else False
        query_id = Long.read(b) if flags & (1 << 0) else None
        url = String.read(b)
        
        return WebViewResultUrl(url=url, fullsize=fullsize, query_id=query_id)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 1) if self.fullsize else 0
        flags |= (1 << 0) if self.query_id is not None else 0
        b.write(Int(flags))
        
        if self.query_id is not None:
            b.write(Long(self.query_id))
        
        b.write(String(self.url))
        
        return b.getvalue()
