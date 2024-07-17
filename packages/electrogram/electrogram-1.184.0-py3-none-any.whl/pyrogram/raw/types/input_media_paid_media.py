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


class InputMediaPaidMedia(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyrogram.raw.base.InputMedia`.

    Details:
        - Layer: ``184``
        - ID: ``AA661FC3``

    Parameters:
        stars_amount (``int`` ``64-bit``):
            N/A

        extended_media (List of :obj:`InputMedia <pyrogram.raw.base.InputMedia>`):
            N/A

    """

    __slots__: List[str] = ["stars_amount", "extended_media"]

    ID = 0xaa661fc3
    QUALNAME = "types.InputMediaPaidMedia"

    def __init__(self, *, stars_amount: int, extended_media: List["raw.base.InputMedia"]) -> None:
        self.stars_amount = stars_amount  # long
        self.extended_media = extended_media  # Vector<InputMedia>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "InputMediaPaidMedia":
        # No flags
        
        stars_amount = Long.read(b)
        
        extended_media = TLObject.read(b)
        
        return InputMediaPaidMedia(stars_amount=stars_amount, extended_media=extended_media)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Long(self.stars_amount))
        
        b.write(Vector(self.extended_media))
        
        return b.getvalue()
