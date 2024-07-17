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


class GetIsPremiumRequiredToContact(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``184``
        - ID: ``A622AA10``

    Parameters:
        id (List of :obj:`InputUser <pyrogram.raw.base.InputUser>`):
            N/A

    Returns:
        List of ``bool``
    """

    __slots__: List[str] = ["id"]

    ID = 0xa622aa10
    QUALNAME = "functions.users.GetIsPremiumRequiredToContact"

    def __init__(self, *, id: List["raw.base.InputUser"]) -> None:
        self.id = id  # Vector<InputUser>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "GetIsPremiumRequiredToContact":
        # No flags
        
        id = TLObject.read(b)
        
        return GetIsPremiumRequiredToContact(id=id)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Vector(self.id))
        
        return b.getvalue()
