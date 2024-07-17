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


class UpdateBroadcastRevenueTransactions(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyrogram.raw.base.Update`.

    Details:
        - Layer: ``184``
        - ID: ``DFD961F5``

    Parameters:
        peer (:obj:`Peer <pyrogram.raw.base.Peer>`):
            N/A

        balances (:obj:`BroadcastRevenueBalances <pyrogram.raw.base.BroadcastRevenueBalances>`):
            N/A

    """

    __slots__: List[str] = ["peer", "balances"]

    ID = 0xdfd961f5
    QUALNAME = "types.UpdateBroadcastRevenueTransactions"

    def __init__(self, *, peer: "raw.base.Peer", balances: "raw.base.BroadcastRevenueBalances") -> None:
        self.peer = peer  # Peer
        self.balances = balances  # BroadcastRevenueBalances

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "UpdateBroadcastRevenueTransactions":
        # No flags
        
        peer = TLObject.read(b)
        
        balances = TLObject.read(b)
        
        return UpdateBroadcastRevenueTransactions(peer=peer, balances=balances)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.peer.write())
        
        b.write(self.balances.write())
        
        return b.getvalue()
