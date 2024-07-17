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


class InputStickerSetThumbLegacy(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyrogram.raw.base.InputFileLocation`.

    Details:
        - Layer: ``184``
        - ID: ``DBAEAE9``

    Parameters:
        stickerset (:obj:`InputStickerSet <pyrogram.raw.base.InputStickerSet>`):
            N/A

        volume_id (``int`` ``64-bit``):
            N/A

        local_id (``int`` ``32-bit``):
            N/A

    """

    __slots__: List[str] = ["stickerset", "volume_id", "local_id"]

    ID = 0xdbaeae9
    QUALNAME = "types.InputStickerSetThumbLegacy"

    def __init__(self, *, stickerset: "raw.base.InputStickerSet", volume_id: int, local_id: int) -> None:
        self.stickerset = stickerset  # InputStickerSet
        self.volume_id = volume_id  # long
        self.local_id = local_id  # int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "InputStickerSetThumbLegacy":
        # No flags
        
        stickerset = TLObject.read(b)
        
        volume_id = Long.read(b)
        
        local_id = Int.read(b)
        
        return InputStickerSetThumbLegacy(stickerset=stickerset, volume_id=volume_id, local_id=local_id)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.stickerset.write())
        
        b.write(Long(self.volume_id))
        
        b.write(Int(self.local_id))
        
        return b.getvalue()
