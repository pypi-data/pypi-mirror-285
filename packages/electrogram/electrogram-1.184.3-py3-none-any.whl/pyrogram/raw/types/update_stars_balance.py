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


class UpdateStarsBalance(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyrogram.raw.base.Update`.

    Details:
        - Layer: ``184``
        - ID: ``FB85198``

    Parameters:
        balance (``int`` ``64-bit``):
            N/A

    """

    __slots__: List[str] = ["balance"]

    ID = 0xfb85198
    QUALNAME = "types.UpdateStarsBalance"

    def __init__(self, *, balance: int) -> None:
        self.balance = balance  # long

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "UpdateStarsBalance":
        # No flags
        
        balance = Long.read(b)
        
        return UpdateStarsBalance(balance=balance)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Long(self.balance))
        
        return b.getvalue()
