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


class BroadcastRevenueStats(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyrogram.raw.base.stats.BroadcastRevenueStats`.

    Details:
        - Layer: ``184``
        - ID: ``5407E297``

    Parameters:
        top_hours_graph (:obj:`StatsGraph <pyrogram.raw.base.StatsGraph>`):
            N/A

        revenue_graph (:obj:`StatsGraph <pyrogram.raw.base.StatsGraph>`):
            N/A

        balances (:obj:`BroadcastRevenueBalances <pyrogram.raw.base.BroadcastRevenueBalances>`):
            N/A

        usd_rate (``float`` ``64-bit``):
            N/A

    Functions:
        This object can be returned by 1 function.

        .. currentmodule:: pyrogram.raw.functions

        .. autosummary::
            :nosignatures:

            stats.GetBroadcastRevenueStats
    """

    __slots__: List[str] = ["top_hours_graph", "revenue_graph", "balances", "usd_rate"]

    ID = 0x5407e297
    QUALNAME = "types.stats.BroadcastRevenueStats"

    def __init__(self, *, top_hours_graph: "raw.base.StatsGraph", revenue_graph: "raw.base.StatsGraph", balances: "raw.base.BroadcastRevenueBalances", usd_rate: float) -> None:
        self.top_hours_graph = top_hours_graph  # StatsGraph
        self.revenue_graph = revenue_graph  # StatsGraph
        self.balances = balances  # BroadcastRevenueBalances
        self.usd_rate = usd_rate  # double

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "BroadcastRevenueStats":
        # No flags
        
        top_hours_graph = TLObject.read(b)
        
        revenue_graph = TLObject.read(b)
        
        balances = TLObject.read(b)
        
        usd_rate = Double.read(b)
        
        return BroadcastRevenueStats(top_hours_graph=top_hours_graph, revenue_graph=revenue_graph, balances=balances, usd_rate=usd_rate)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.top_hours_graph.write())
        
        b.write(self.revenue_graph.write())
        
        b.write(self.balances.write())
        
        b.write(Double(self.usd_rate))
        
        return b.getvalue()
