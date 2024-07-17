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


class PeerColors(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyrogram.raw.base.help.PeerColors`.

    Details:
        - Layer: ``184``
        - ID: ``F8ED08``

    Parameters:
        hash (``int`` ``32-bit``):
            N/A

        colors (List of :obj:`help.PeerColorOption <pyrogram.raw.base.help.PeerColorOption>`):
            N/A

    Functions:
        This object can be returned by 2 functions.

        .. currentmodule:: pyrogram.raw.functions

        .. autosummary::
            :nosignatures:

            help.GetPeerColors
            help.GetPeerProfileColors
    """

    __slots__: List[str] = ["hash", "colors"]

    ID = 0xf8ed08
    QUALNAME = "types.help.PeerColors"

    def __init__(self, *, hash: int, colors: List["raw.base.help.PeerColorOption"]) -> None:
        self.hash = hash  # int
        self.colors = colors  # Vector<help.PeerColorOption>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "PeerColors":
        # No flags
        
        hash = Int.read(b)
        
        colors = TLObject.read(b)
        
        return PeerColors(hash=hash, colors=colors)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Int(self.hash))
        
        b.write(Vector(self.colors))
        
        return b.getvalue()
