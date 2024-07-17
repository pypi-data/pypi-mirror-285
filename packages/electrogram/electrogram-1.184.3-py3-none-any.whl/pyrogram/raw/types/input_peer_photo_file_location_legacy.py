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


class InputPeerPhotoFileLocationLegacy(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyrogram.raw.base.InputFileLocation`.

    Details:
        - Layer: ``184``
        - ID: ``27D69997``

    Parameters:
        peer (:obj:`InputPeer <pyrogram.raw.base.InputPeer>`):
            N/A

        volume_id (``int`` ``64-bit``):
            N/A

        local_id (``int`` ``32-bit``):
            N/A

        big (``bool``, *optional*):
            N/A

    """

    __slots__: List[str] = ["peer", "volume_id", "local_id", "big"]

    ID = 0x27d69997
    QUALNAME = "types.InputPeerPhotoFileLocationLegacy"

    def __init__(self, *, peer: "raw.base.InputPeer", volume_id: int, local_id: int, big: Optional[bool] = None) -> None:
        self.peer = peer  # InputPeer
        self.volume_id = volume_id  # long
        self.local_id = local_id  # int
        self.big = big  # flags.0?true

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "InputPeerPhotoFileLocationLegacy":
        
        flags = Int.read(b)
        
        big = True if flags & (1 << 0) else False
        peer = TLObject.read(b)
        
        volume_id = Long.read(b)
        
        local_id = Int.read(b)
        
        return InputPeerPhotoFileLocationLegacy(peer=peer, volume_id=volume_id, local_id=local_id, big=big)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.big else 0
        b.write(Int(flags))
        
        b.write(self.peer.write())
        
        b.write(Long(self.volume_id))
        
        b.write(Int(self.local_id))
        
        return b.getvalue()
