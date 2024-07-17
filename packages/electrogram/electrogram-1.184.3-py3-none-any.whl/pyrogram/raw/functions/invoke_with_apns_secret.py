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


class InvokeWithApnsSecret(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``184``
        - ID: ``0DAE54F8``

    Parameters:
        nonce (``str``):
            N/A

        secret (``str``):
            N/A

        query (Any function from :obj:`~pyrogram.raw.functions`):
            N/A

    Returns:
        Any object from :obj:`~pyrogram.raw.types`
    """

    __slots__: List[str] = ["nonce", "secret", "query"]

    ID = 0x0dae54f8
    QUALNAME = "functions.InvokeWithApnsSecret"

    def __init__(self, *, nonce: str, secret: str, query: TLObject) -> None:
        self.nonce = nonce  # string
        self.secret = secret  # string
        self.query = query  # !X

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "InvokeWithApnsSecret":
        # No flags
        
        nonce = String.read(b)
        
        secret = String.read(b)
        
        query = TLObject.read(b)
        
        return InvokeWithApnsSecret(nonce=nonce, secret=secret, query=query)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(String(self.nonce))
        
        b.write(String(self.secret))
        
        b.write(self.query.write())
        
        return b.getvalue()
