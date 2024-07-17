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


class BroadcastRevenueTransactions(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyrogram.raw.base.stats.BroadcastRevenueTransactions`.

    Details:
        - Layer: ``184``
        - ID: ``87158466``

    Parameters:
        count (``int`` ``32-bit``):
            N/A

        transactions (List of :obj:`BroadcastRevenueTransaction <pyrogram.raw.base.BroadcastRevenueTransaction>`):
            N/A

    Functions:
        This object can be returned by 1 function.

        .. currentmodule:: pyrogram.raw.functions

        .. autosummary::
            :nosignatures:

            stats.GetBroadcastRevenueTransactions
    """

    __slots__: List[str] = ["count", "transactions"]

    ID = 0x87158466
    QUALNAME = "types.stats.BroadcastRevenueTransactions"

    def __init__(self, *, count: int, transactions: List["raw.base.BroadcastRevenueTransaction"]) -> None:
        self.count = count  # int
        self.transactions = transactions  # Vector<BroadcastRevenueTransaction>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "BroadcastRevenueTransactions":
        # No flags
        
        count = Int.read(b)
        
        transactions = TLObject.read(b)
        
        return BroadcastRevenueTransactions(count=count, transactions=transactions)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Int(self.count))
        
        b.write(Vector(self.transactions))
        
        return b.getvalue()
