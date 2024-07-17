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


class InvokeWithGooglePlayIntegrity(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``184``
        - ID: ``1DF92984``

    Parameters:
        nonce (``str``):
            N/A

        token (``str``):
            N/A

        query (Any function from :obj:`~pyrogram.raw.functions`):
            N/A

    Returns:
        Any object from :obj:`~pyrogram.raw.types`
    """

    __slots__: List[str] = ["nonce", "token", "query"]

    ID = 0x1df92984
    QUALNAME = "functions.InvokeWithGooglePlayIntegrity"

    def __init__(self, *, nonce: str, token: str, query: TLObject) -> None:
        self.nonce = nonce  # string
        self.token = token  # string
        self.query = query  # !X

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "InvokeWithGooglePlayIntegrity":
        # No flags
        
        nonce = String.read(b)
        
        token = String.read(b)
        
        query = TLObject.read(b)
        
        return InvokeWithGooglePlayIntegrity(nonce=nonce, token=token, query=query)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(String(self.nonce))
        
        b.write(String(self.token))
        
        b.write(self.query.write())
        
        return b.getvalue()
