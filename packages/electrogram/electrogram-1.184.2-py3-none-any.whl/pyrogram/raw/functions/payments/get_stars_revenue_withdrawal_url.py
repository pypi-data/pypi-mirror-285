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


class GetStarsRevenueWithdrawalUrl(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``184``
        - ID: ``13BBE8B3``

    Parameters:
        peer (:obj:`InputPeer <pyrogram.raw.base.InputPeer>`):
            N/A

        stars (``int`` ``64-bit``):
            N/A

        password (:obj:`InputCheckPasswordSRP <pyrogram.raw.base.InputCheckPasswordSRP>`):
            N/A

    Returns:
        :obj:`payments.StarsRevenueWithdrawalUrl <pyrogram.raw.base.payments.StarsRevenueWithdrawalUrl>`
    """

    __slots__: List[str] = ["peer", "stars", "password"]

    ID = 0x13bbe8b3
    QUALNAME = "functions.payments.GetStarsRevenueWithdrawalUrl"

    def __init__(self, *, peer: "raw.base.InputPeer", stars: int, password: "raw.base.InputCheckPasswordSRP") -> None:
        self.peer = peer  # InputPeer
        self.stars = stars  # long
        self.password = password  # InputCheckPasswordSRP

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "GetStarsRevenueWithdrawalUrl":
        # No flags
        
        peer = TLObject.read(b)
        
        stars = Long.read(b)
        
        password = TLObject.read(b)
        
        return GetStarsRevenueWithdrawalUrl(peer=peer, stars=stars, password=password)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.peer.write())
        
        b.write(Long(self.stars))
        
        b.write(self.password.write())
        
        return b.getvalue()
