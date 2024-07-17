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


class MessageActionGiveawayResults(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyrogram.raw.base.MessageAction`.

    Details:
        - Layer: ``184``
        - ID: ``2A9FADC5``

    Parameters:
        winners_count (``int`` ``32-bit``):
            N/A

        unclaimed_count (``int`` ``32-bit``):
            N/A

    """

    __slots__: List[str] = ["winners_count", "unclaimed_count"]

    ID = 0x2a9fadc5
    QUALNAME = "types.MessageActionGiveawayResults"

    def __init__(self, *, winners_count: int, unclaimed_count: int) -> None:
        self.winners_count = winners_count  # int
        self.unclaimed_count = unclaimed_count  # int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "MessageActionGiveawayResults":
        # No flags
        
        winners_count = Int.read(b)
        
        unclaimed_count = Int.read(b)
        
        return MessageActionGiveawayResults(winners_count=winners_count, unclaimed_count=unclaimed_count)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Int(self.winners_count))
        
        b.write(Int(self.unclaimed_count))
        
        return b.getvalue()
