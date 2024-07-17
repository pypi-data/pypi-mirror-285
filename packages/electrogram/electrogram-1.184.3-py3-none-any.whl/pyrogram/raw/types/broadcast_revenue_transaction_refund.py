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


class BroadcastRevenueTransactionRefund(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyrogram.raw.base.BroadcastRevenueTransaction`.

    Details:
        - Layer: ``184``
        - ID: ``42D30D2E``

    Parameters:
        amount (``int`` ``64-bit``):
            N/A

        date (``int`` ``32-bit``):
            N/A

        provider (``str``):
            N/A

    """

    __slots__: List[str] = ["amount", "date", "provider"]

    ID = 0x42d30d2e
    QUALNAME = "types.BroadcastRevenueTransactionRefund"

    def __init__(self, *, amount: int, date: int, provider: str) -> None:
        self.amount = amount  # long
        self.date = date  # int
        self.provider = provider  # string

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "BroadcastRevenueTransactionRefund":
        # No flags
        
        amount = Long.read(b)
        
        date = Int.read(b)
        
        provider = String.read(b)
        
        return BroadcastRevenueTransactionRefund(amount=amount, date=date, provider=provider)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Long(self.amount))
        
        b.write(Int(self.date))
        
        b.write(String(self.provider))
        
        return b.getvalue()
